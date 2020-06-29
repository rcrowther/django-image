# Django-images
A drop and go app (as much as a Django app can be) to handle upload and display of images in Django.

The base code is concise and levers Django recommentions and facilities where possible. It may form a good base for others wishing to build their own app.

The front end, by which I mean 'programmer API' is designed for a particular purpose (most image apps are). It is for webistes where images are associated with other models. Use cases might include websites of local interest, such as small-scale publishing and shops. These examples would associate images with other models, for example, SalesItem or Article.


## Why you may not want this app
This may not be the app for you.

<div style="border:2px solid green; border-radius: 12px;">
The app API does not let you write template tags with adjustable parameters, filters with runtime parameter processing, create filter chains, or categorise/tag images.
</div>

All these facilities can be built in to the base code. But then the app wil not be, for you, a plug and go solution.
 
The code API is a step back from the facilities mentioned above. It is small, concise, and fits good CSS/template-practice. 


Also, I have not,
- considered SVG images
- tested cloud storage


## Overview
Images are tracked in the database. The base model is called 'Image'. 

Each original image can generate derivitive images. These are tracked by a model called 'Reform'. Reforms are generated by filters. Filters can be defined in apps or centrally. 

Image delivery is by template tag. The presence of a tag with a reference to an image and a filter will generate a reform automatically. The tags deliver images by URL.

File-based storage is in 'media/' with paths adjustable through attribute settings.

The app includes code to upload images. The Django admin for the base application has some (optional) customisation.



## If you have done this before
Decide if you want to use the core collection. If you want an app-based collection, [subclass the models for Image and Reform](#new-image-repositories).

[Add fields](#model-fields) to models that need them.

[Add auto deletion](#Autodeletion) if you want models carrying image fields to delete images automatically.

Migrate new tables.

Create a file called 'image_filters.py' in the app. [Sublass a few filters](#filters),

Insert [template tags](#template-tags) into the relevant templates,

    {% load img_tags %}

    ...

    {% image a_model.a_field my_app.FilterName %}






## Quickstart
### Depemdancies
Unidecode,

    pip unidecode

[Unidecode](https://pypi.org/project/Unidecode/)

Pillow,

    pip pillow

[Pillow](https://pillow.readthedocs.io/en/stable/index.html)


#### Optional
The code API can work with other image libraries such as Wand and OpenCV. Some Wand filters are built-in. On Debian-based distros,

    sudo apt-get install libmagickwand-dev

Then,

    pip install wand

The built-in Wand filters offer more image-processing options.



### Install
Download the app code to Django

Declare in Django settings,

        INSTALLED_APPS = [
            ...
            'image.apps.ImageConfig',
            ...
        ]

migrate now,

    ./manage.py makemigrations image
    ./manage.py migrate image

If you have Django Admin, you can now upload images.



### Upload some images
In Django admin, go to Image upload and try upload a few images.

I don't know about you, but if I have a new app I like to try with real data. If you have a collection of test images somewhere, try this management command,

    ./manage.py image_create_bulk pathToMyDirectory

You can create, meaning upload and register, fifteen or twenty images in a few seconds.



### View some images
Ok, let's see an image, as you would on site. Two ways.

#### Use a view 
Find a web view template. Nearly any template will do (maybe not a JSON REST interface, something visible).

Add this tag to the template,

    {% load img_tags %}
    ...
    {% imagequery "pk=1" image.Thumb %}

'image.Thumb' is a predefined filter. It makes a 64x64 pixel Thumbnail. The tag we use here searchs for an image by a very low method, "pk=1". This will do for now.  

Visit the page. The app will generate the filtered 'reform' image automatically, To change how the image is filtered, size and so on, see Filters.


#### Don't have a view?
Yeh, new or experimental site, I know. Image has a builtin view. Goto urls.py, add this,

    path('image/<int:pk>/', ImageDetailView.as_view(), name='image-detail'),

Now visit (probably),

    http://localhost:8000/image/1/

To see some *real* web code.


### (aside) Filters
Perhaps your first request will be how to make a new filter.

Make a new file called 'image filters'. Put it in the top level of any app, or in the site folder (alongside url.py and wsgi.py). Put something in it like this (adapt if you wish),

    from image import Resize, registry

    class MediumImage(Resize)
        width=260
        height=350
        format='png'

    registry.register(MediumImage)
 
Now adapt the template tag (or the tag in image/templates/image/image_detail.html) to point at the new filter,

    {% imagequery "pk=1" someAppName.MediumImage %}

Visit the page again. Image sees the new filter definition, finds it has no record of a reform for that image and filter, so generates a new one, then displays it.

Ok, you changed the image size, and maybe the format. If you want to continue, you probably have questions. Goto the main documentation.



## QuickStop
Don't like what you see?

- Remove any temporary code.
- Migrate backwards,

    ./mangage.py migrate image zero
- Remove from apps.py
- Remove the two directories in /media,

    originals/
    reforms/

- Remove the app folder.

That's it, gone.



## Full documentation
The documenation is split into general areas. 

- [Model Fields](#model-fields)
- [New Image Repositories](#new-image-repositories)
- [Filters](#filters)
- [Admin](#admin)
- [Forms](#forms)
- [Template Tags](#template-tags)
- [Management Commands](#management-commands)
- [Settings](#settings)
- [Utils](#utilities)


## Model Fields
Two ways,

#### The ImageRelationFieldMixin model fields
There are two, ImageManyToOneField and ImageOneToOneField,

    from image.model_fields import ImageManyToOneField


    class Page(models.Model):

        img = ImageManyToOneField(
            'page.Image'
            )

#### Stock Django declaration,
You can also use a stock Django foreign key declaration,

    from image.models import Image


    class Page(models.Model):

        img = models.ForeignKey(
            'page.Image',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name='+'
            )

         etc.

null=True and blank=True means you can delay adding an image until later. And related_name='*' means that Images will not track the models you are creating. See Django documentation of model fields for more details.

Only use models.CASCADE if you are sure this is what you want. It means, if an image is deleted, your model that carries the image is deleted too. This is usually not what you want.


#### Choosing between the two
ImageOneToOneField/ImageManyToOneField
- tidy
- Work with preconfigured admin and auto-delete

Foreign Field
- Django stock
- explicit
- flexible configuration


### Auto-delete
The solution only works if the model uses fields with the ImageRelationFieldMixin i.e. ImageManyToOneField and ImageOneToOneField.

Add this to your app.ready(),

    from image.actions import _image_delete

    def ready()
        post_delete.connect(_image_delete, sender=SomeModel, weak=False)


The above settings will remove images when the model is deleted. If you prefer,




## New Image Repositories
### Overview
The two core models in this app can be subclassed. If you create subclasses, the subclass models have new DB tables, and can operate with new configurations such as storing files in different directories.

Two scenarios where you may want to do this,

#### Associated data with images
You may want to associate data with an image. Many people's first thought would be a title. That said, an image title is not often displayed, and/or a simple duplication of a filename, which should be avoided. Image does not provide titles by default.

But other kinds of information can be attached such as captions, credits, dates, and/or data for semantic rendering. All of these can legitimately viewed as 'part of the image' or 'an aspect of the image'.

#### Splitting needs
Its fun to tweak with settings, but sometimes, maybe often, this is not the best approach.

Let's say you have a website which gathers photos that are joined to NewsArticle. Those photos are linked for sure to the Article, and can probably be created and deleted with the NewsArticle. But you may also have a need to upload images for the site in general. Perhaps for banner displays. This is an image pool. The deletion policy is different. There may be no need for credits.
 
These are two seperate apps. Make two apps. Avoid complex configuration.

### Subclassing Image/Reform 
In the models.py file in an app, do this. 

    from image.models import AbstractImage, AbstractReform

    class NewsArticleImage(AbstractImage):
        upload_dir='news_originals'

        #! Must be migrated
        filepath_length=100

        #! in subclasses, must be enabled with a post_save signal. 
        auto_delete_files=True

        # AbstractImage has a file and upload_date
        caption = models.CharField(_('Caption'),
            max_length=255,
        )

        author = models.CharField(_('Author'),
            max_length=255,
            db_index=True
        )

        etc.



    class NewsArticleReform(AbstractReform):
        image_model = NewsArticleImage
        upload_dir='news_reforms'
        filepath_length=100


Not the last word in DRY coding, but you should be able to work out what the code is doing. Note the configuration variables. Useful. Think about them before you migrate.

Then migrate,

    ./manage.py migrate NewsArticle

You now have a new image upload app. It has it's own DB tables. Change it's configuration. Refer to it in other models,

    class NewsArticle(models.Model):

        img = ImageManyToOneField(
            "news_article.NewssArticleImage"
            )

        etc.

### Things to consider with subcalsses of models
#### Auto-delete
Let's say that when an image model is deleted, you want to auto-delete the file (Django used to do this, now it does not). The core implementation in this app auto-deletes,  but subclasses will not. If you want a subclass to auto-delete, set 'autto_delete_files = True' in the image subclass, then add this to app.py,


    from image.signals import register_file_delete_handlers

    def ready()
        super().ready()
        from models import NewsArticleImage, NewsArticleReform          
        register_file_delete_handlers(NewsArticleImage, NewsArticleReform)


Note the position of the model import. It must be in the ready callback, not the main module.

 
#### Add Meta information
You may want to configure a Meta. If you have titles or slugs, for example, you may be interested in making them into unique constrained groups or adding indexes,

    class NewssArticleImage(AbstractImage):
        upload_dir='news_originals'
        filepath_length=100

        etc.

        class Meta:
            verbose_name = _('news_image')
            verbose_name_plural = _('news_images')
            indexes = [
                models.Index(fields=['author']),
            ]
            constraints = [
                models.UniqueConstraint(
                    fields=['title', 'author'], 
                    name='unique_newsarticle_reform_src'
                )



## Filters
### Overview
Filters are used to describe how an original uploaded image should be modified for display. In the background, the app will automatically adjust the image to the given spacification (or use a cached version).
 
A few filters are predefined. A couple of utility filters,

Format
    Change the format of an uploaded image
Thumb
    A 64x64 pixel square

And some base filters, which you can configure. These are all centre-anchored, 

- Crop
- Resize
- SmartCrop
- SmartResize

If you only need different image sizes, then you only need to configure these. But if you want to pass some time with image-processing code, you can add extra filters to generate ''PuddingColour' and other filters.


### Filter placement and registration
Files of filter definitions can be placed in any app. Start a file called 'image_filters.py' and off you go.

If you would prefer to gether all filters together in one place, define the settings to include,

    Image : {
            'MODULES': [
                        "siteName",
            ],
    }

Then put a file image_filters.py in the 'sitename' directory. If you do this, you should namespace the filters,

    BlogPostLarge:
        width : 256
        height 256


### Filter declarations
All builtin filter bases accept these attributes,

- width
- height
- format

Most filter code demands width and height, but format is optional. Without a stated format, the image stays as it was (unless another setting is in place). Formats accepted are,

    gif, png, jpg, bmp, tiff, webp 

which should be written as above (lowercase, and 'jpg', not 'jpeg'). So,

    from image import Resize, registry

    class MediumImage(Resize)
        width=260
        height=350
        format='png'

    registry.register(MediumImage)


Crop and Resize can/often result in images narrower in one dimension. 

The Smart variations do a background fill in a chosen colour, so return the requaeted size,

    from image import ResizeSmart, registry

    class MediumImage(ResizeSmart):
        width=260
        height=350
        format='jpg'
        fill_color="Coral"

    registry.register(MediumImage)

Fill color is defined however the image library handles it. Both Pillow and Wand can handle CSS style hex e.g. '#00FF00' (green), and HTML colour-names e.g. 'AliceWhite'.


### Registering filters
Filters need to be registered. Registration style is like ModelAdmin, templates etc. Registration is to the image.registry (this is how templatetags finds them).

You can use the declaration used in the examples above,

    from image import ResizeSmart, registry

    ...

    registry.register(single_or_list_of_filters)

Like ModelAdmin, there is also a decorator available,

    from image import register, ResizeSmart

    @register()
    class MediumImage(ResizeSmart):
        width=260
        height=350
        format='jpg'
        fill_color="Coral"


### Wand filters
The base filters in the Wand filter set have more attributes available. The 'wand' code needs Wand to be installed on the host computer, and a imported into the image_filters file. Assuming that, you gain these effects on every Wand filter,

    from image import registry
    from image.wand_filters import ResizeSmart

    class MediumImage(ResizeSmart):
        width=260
        height=350
        format='jpg'
        pop=False
        greyscale=False
        night=False
        warm=False
        strong=False
        no=False
        watermark=None # e.g.'/srv/images/watermark.png'

    registry.register(Medium)


If you enable more than one effect, they will chain, though you have no control over order.

I lost my way with the Wand effects. There is no 'blur', no 'rotate', no 'waves'. But there is,

pop
    Tightens leveling of black and white
greyscale
    A fast imitation
night
    Pretend the picture is from a movie
warm
    A small shift in hue to compensate for a common photography white-balance issue. 
strong
    Oversaturate image colors (like everyone does on the web). Unlike 'pop' this will not stress contrast so flatten blacks and whites. You may or may not prefer this. 
no
    Draw a red cross across the image
watermark
    Accepts a URL to a watermark image template.

Watermark deserves some explanation. This does not draw on the image, as text metrics are tricky to handle. Provide a URL stub to an image, here's a builtin,

    watermark = 'image/watermark.png'

The URL is Django static-aware, but will pass untouched if you give it a web URL (like the URLs in Django Media).
 
The template is scaled to the image-to-be-watermarked, then composited over the main image by 'disolve'. So the watermark is customisable, can be used on most sizes of image, and is usually readable since aspect ratio is preserved.

It is probably worth saying again that you can not change the parameters, so the strengths of these effects, without creating a new filter.


### Writing custom filter code
First bear in mind that Image uses fixed parameters. So your filter must work with fixed parameters across a broad range of uploaded images. I don't want anyone to dive into code, put in hours of work, then ask me how they can create an online image-editing app. Not going to happen.

However, while I can't make a case for 'waves' or 'pudding-colour' filters, I can see uses. For example, Wagtail CMS uses the OpenCV library to generate images that auto-focus on facial imagry (i.e. not centrally crop). There are uses for that.

Second, bear in mind that image editing is lunging into another world, rather like creating Django forms without using models and classes. It will take time. But there is help available.
 
Inherit from image.Filter. You will need to provide a 'process' method, which takes an open Python File and returns a ByteBufferIO and a file extension.

If you want the filter to work with the Pillow or Wand liraries, you can inherit from the PillowMixin or WandMixin. These cover filehandling for those libraries. so you can provide a 'modify' method, which alters then returns an image in the format of those libraries.

See the code for details.


### Why can filters not be chained?
Filters can not be chained dynamically. There is no way to present chaining to a user. You need to create a fixed filter. Filters must be written in code, and do not accept parameters. You want a filter with new parameters, you write it and it is set.

This is a deliberate decision. It makes life easy. If you want to produce a front-end that can lever the filters and chain them, that is another step. This is not that app.






## Admin
### Overview
Image ships with stock Django admin. However, this is not always suited to the app, it's intended or possible uses. So there are some additions.

The admin provided has an attitude about how to use the app.

<div style="border:2px solid green; border-radius: 12px;">
The custom admin assumes that each model instance is locked to one file. If a model exists, then the file exists. If the admin is given the same file, it duplicates file and model.
</div>

In this system, models that use the Image models are still free to be null and blank, to represent 'image not yet uploaded'. And it is possible to build systems that reuse images---it is the Image_instance->file connection that is locked.


### Package solutions
#### ImageCoreAdmin
For administration and maintenance of the image collections. This is a rather specialised use, which would only be visible to end users if they are trusted.

If you go to the admin.py file in the app, you will find an alternative Admin file builtin. This is for handling the images and image DB itself (not images attached to models in other apps),

    # Custom admin interface disalows deletion of files from models.
    #class ImageAdmin(ImageCoreAdmin):
        
    # Stock admin interface.
    class ImageAdmin(admin.ModelAdmin):
        pass
            
            
    admin.site.register(Image, ImageAdmin)

If you'd like to try the core admin, change the comments,

    # Custom admin interface disalows deletion of files from models.
    class ImageAdmin(ImageCoreAdmin):
        
    # Stock admin interface.
    #class ImageAdmin(admin.ModelAdmin):
        pass
        
        
    admin.site.register(Image, ImageAdmin)

The modified app makes several changes to the builtin Admin. A short list of significant changes,

- changelist is tidier and includes view links
- changelist has searchable titles
- upload form prepopulates the new title with the filename 
- change form disables Image choice


##### Notes and alternatives for the core admin
You may provide no core admin at all. You can use the ./manage.py commands to do maintenence. The stock admin is provided to get you started.

IF you prefer your own core admin, have a look at the code for ImageCoreAdmin in '/image/admins.py'. It provides some useful clues about how to do formfield overrides, and other customisations.

If using subclassed Image/Reform models, you may find it more maintainable to duplicate and modify the admin code, rather than import and override.


#### LinkedImageAdmin
For administration of models that contain foreign key links to images.

This is a small override that should not interfere with other admin code. It disallows image editing once an image has been connected to a field (by upload or selection). e.g.

    from image.addmins import LinkedImageAdmin

        class NewsArticleAdmin(LinkedImageAdmin, admin.ModelAdmin):
            pass
            
            
        admin.site.register(NewsArticle, NewsArticleAdmin)



## Forms
There's nothing special about using the Image model in forms. Stock Django. Use the model via Django admin or Model forms. For your own forms, the Image model contains some extra validators, they are on the models so a call to is_valid() will run them.

### Form parts
Both the below are used in the base Image model. They are no use unless you you are building forms to control Image models directly (rare).

#### Model Fields
FreeImageField. Loads a FreeImageField as default (see below).

#### Form Field
FreeImageField. This skips path length verification on forms. Both this module, AND Django core, set and truncate lengths on upload. If you prefer that a user can upload files with any length of filename, but that the filename will be truncated, then use this.


 
## Template Tags
### Overview
For most uses, the app only has one template tag. There is another, for testing and edge cases.

## The 'image' tag
You define a filter called ''Large'. Add this to template code,

    {% load img_tags %}

    {% image report.img my_app.Large %}
 
then visit the page. The app will generate a ''Large' reform of 'report.image', to the spec given in the filter.

The tag guess can guess the app from the context. So,

     {% image report.img Large %}

Will assume the filter is in the app the context says the view comes from.

The tag accpts keyword parameters which become HTML attributes,

     {% image report.img Large class="report-image" %}
     <caption>{{ page.img.title }}</caption>

Assuming a title "End Of Year Table", this renders similar to,

    <img src="/media/reforms/eoy-report_large.png" alt="end of year table image" class="report-image">
    <caption>End Of Year Table</caption>


### The 'query' tag
There is a tag to find images by a database query. Sometimes this will be useful, for fixed or temporary decoration/banners etc. 

        {{ imagequery "query" image.Large  }}

While this may be useful, especially for fixed logos or banners, it is unnecessary if you are passing a model through a context,


### Filters from other apps
You can borrow filter collections from other apps. Use the module path and filter classname,

    {% image "urban_decay" different_app.filter_name  %} 

But try not to create a tangle between your apps. You would not do that with CSS or other similar resources. Store general filters in a central location, and namespace them.



## Management Commands
They are,

- image_create_bulk
- image_sync
- image_list
- reform_delete

All management commands can be pointed at subclasses of Image and Reform, as well as the default app models.

They do what they say. 'image_sync' is particularly useful, it will attempt to make models for orphaned files, or delete orphaned files, or delete models with missing files. These commands are useful for dev, too.





## Settings
### Overview
Image accepts settings in several places. The app has moved away from using the site-wide settings.py towards other placements, with consistent override behaviour. Here is a summary, in order of last placement wins,

### Image
upload_dir
    default='originals', Image attribute
    
filepath_length
    default=100, Image attribute, (if overridden) Image field 
        
auto_delete_files
    (if enabled) Image/Reform attribute

max_upload_size
    default=2MB, Image attribute


### Reform
upload_dir
    default='reforms', Reform attribute

filepath_length
    default=100, Reform attribute, (if overridden) Reform field 
            
image_model
    default='image.Image', Reform attribute

file_format
    default=original format, Reform attribute, filter attribute

jpeg_quality
    default=80, Reform attribute, filter attribute



### Site-wide settings
Images accepts some site-wide settings. They look like the Django template settings,

    IMAGES = [
        {
            'SEARCH_APP_DIRS': True,
            'SEARCH_MODULES': [
                        "someSiteName",
            ],
        },
    ]

SEARCH_APP_DIRS
Find 'image_filters.py' files in apps. If False, the app only uses filters defined in the core app and SEARCH_MODULES setting.

SEARCH_MODULES
Defines extra places to find 'image_filter.py' files. The above example suggests a site-wide filter collection in the site directory (most page-based Django sites have central collections of templates and CSS in the same directory). The setting takes module paths, not filepaths, because 'image_filter.py' files are live code.





    
        
## Utilities
### The View
Image has a builtin view. It's main purpose is to test filter code. The view template reforms from images in the core folder. As a test and trial device, it is not enabled by default.

Goto urls.py, add this,

    path('image/<int:pk>/', ImageDetailView.as_view(), name='image-detail'),

Now visit (probably),

    http://localhost:8000/image/1/

The template is at,

    image/templates/image/image_detail.html

Where you can edit the template tag to point at your own configurations. With visible results and basic image data, it is a lot easier to use than the shell.


## Issues
No SVG support 
: requires shadow code, Pillow especially can't handle them

Widths, heights and bytesize of original images are recorded, in case the storage media is not local files but cloud provision.

The app uses the URL attribute of the FileFields to generate HTML 'src' (not the filepath). So it should keep working if you swap storage backends or, at least, keep responding an a Django-like way.


## Credits
The upload and storage code (particularly the replicable models) was ripped from the Wagtail CMS. Though I am responsibile for how I have treated it.

[Wagtail documentation](https://docs.wagtail.io/en/v2.8.1/advanced_topics/images/index.html)

