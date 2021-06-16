from haystack import indexes

from main_app.models import File


class FileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    file_id = indexes.IntegerField(model_attr="file_id")
    name = indexes.NgramField(model_attr="name")
    file = indexes.NgramField(model_attr="file")

    class Meta:
        model = File
        fields = ("file",)

    def get_model(self):
        return File

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_name(self, obj):
        return obj.name

    def prepare_file(self, obj):
        f = open(obj.file.path, "r")
        lines = f.read()
        result = []

        for word in lines.split():
            result.append(word)
        f.close()
        return result
