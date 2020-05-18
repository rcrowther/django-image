from image.models import Reform, SourceImageIOError
import os.path
from django.templatetags.static import static

# cache
def image_broken_url():
    '''
    Deliver a static-aware 'broken url' path.
    '''
    return static('image/unfound.png')
     
def get_reform_or_not_found(image, ifilter):
    """
    Tries to get / create the reform for the image or renders a 
    not-found image if it does not exist.
    :param image: AbstractImage instance
    :param filter_id: str or Filter
    :return: Reform
    """
    try:
        return image.get_reform(ifilter)
    except SourceImageIOError:
        # (probably) SourceImageIOError indicates an Image is missing 
        # it's file. Instead of throwing a whole page error, make a mock
        # reform to hold a generic broken image.
        # A textlike 'name' parameter triggers no attempt to 'upload'.
        fp = image_broken_url()
        reform = Reform(image=image)
        reform.src.name = fp
        return reform
