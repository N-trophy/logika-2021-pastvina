from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from os import path, rename


class User(AbstractUser):
    first_name = None
    last_name = None
    team_name = models.CharField(max_length=255)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField("vytvořeno", default=timezone.now, editable=False)
    updated = models.DateTimeField("upraveno", default=timezone.now, editable=False)

    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        super().save(*args, **kwargs)

        return self


class PublishableModel(BaseModel):
    class Meta:
        abstract = True

    published = models.BooleanField("publikováno", default=False, blank=True)
    public_from = models.DateTimeField("publikováno od", null=True, blank=True)
    public_to = models.DateTimeField("publikováno do", null=True, blank=True)

    def is_public(self):
        if not self.published:
            return False
        if self.public_from and self.public_from >= timezone.now():
            return False
        if self.public_to and self.public_to <= timezone.now():
            return False
        return True

    @staticmethod
    def q_public():
        return Q(Q(public_to__gte=timezone.now()) | Q(public_to=None),
                 Q(public_from__lte=timezone.now()) | Q(public_from=None),
                 published=True)

    @classmethod
    def public_objects(cls):
        return cls.objects.filter(PublishableModel.q_public())


class Contribution(PublishableModel):
    class Meta:
        verbose_name = 'novinka'
        verbose_name_plural = 'novinky'

    name = models.CharField('název', max_length=60)
    text = models.TextField('text novinky')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='autor')
    tags = models.TextField('tagy', default="", blank=True)

    def tag_list(self):
        return [t.strip().split('#') if '#' in t else (t, None) for t in self.tags.split(',') if t.strip()]

    def tag_list_str(self):
        tags = self.tag_list()
        if not tags:
            return ''
        else:
            return ' | '.join(list(zip(*self.tag_list()))[0])


class StaticPage(BaseModel):
    class Meta:
        verbose_name = 'statická stránka'
        verbose_name_plural = 'statické stránky'
    
    endpoint = models.CharField('URL lokace', max_length=30)
    title = models.CharField('title', max_length=30)
    name = models.CharField('název v menu', max_length=30)
    content = models.TextField('obsah')

    def save(self, *args, **kwargs):
        if not self.endpoint or self.endpoint[0] != '/':
            self.endpoint = '/' + self.endpoint
        if self.endpoint[-1] != '/':
            self.endpoint += '/'
        super(StaticPage, self).save(*args, **kwargs)


class MediaFile(BaseModel):
    class Meta:
        verbose_name = 'soubor'
        verbose_name_plural = 'soubory'
    
    @staticmethod
    def userid_from_filename(filename):
        return filename.split('__')[0]

    def path_in_storage(self, fname=None):
        if fname and '.' in fname:
            ext = '.' + fname.split('.')[-1]
        else:
            ext = ''
        
        if self.public:
            return path.join(settings.MEDIA_DIR_NAME, "{0}{1}".format(self.name, ext))
        else:
            return path.join(settings.PRIVATE_DIR_NAME, "{0}__{1}__{2}{3}".format(self.owner.id,
                                                                                  self.created.strftime('%Y-%m-%d-%H%M'),
                                                                                  self.name, ext))
    
    def save(self, *args, **kwargs):
        if self.content.storage.exists(self.content.name):
            new_path = self.content.storage.path(self.path_in_storage(self.content.name))
            rename(self.content.path, new_path)
            self.content.name = self.path_in_storage(self.content.name)

        super(MediaFile, self).save(*args, **kwargs)

    public = models.BooleanField('veřejné')
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='vlastník')
    content = models.FileField('soubor', upload_to=path_in_storage, storage=FileSystemStorage(settings.STORAGE_ROOT,
                                                                                              settings.STORAGE_URL))
    name = models.SlugField('jméno', max_length=60, unique=True)


class Menu(models.Model):
    class Meta:
        verbose_name = 'menu'
        verbose_name_plural = 'menu'

    name = models.CharField('jméno', max_length=30)
    pages = models.ManyToManyField(StaticPage)
    locations = models.TextField('lokace')
