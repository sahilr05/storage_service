# products/search_indexes.py
from haystack import indexes

from main_app.models import File


class FileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    file_id = indexes.IntegerField(model_attr="file_id")
    file = indexes.CharField(model_attr="file")

    class Meta:
        model = File
        fields = ("file",)

    def get_model(self):
        return File

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
