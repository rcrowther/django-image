def register():
    """
    Register the given classes and wrapped ModelAdmin class with
    admin site:

    @register()
    class AuthorAdmin(admin.ModelAdmin):
        pass
    """
    from image import Filter, registry

    def _filter_wrapper(filter_class):

        if not issubclass(filter_class, Filter):
            raise ValueError('Wrapped class must subclass image.Filter.')
            
        registry.register(filter_class)

        return filter_class

    return _filter_wrapper