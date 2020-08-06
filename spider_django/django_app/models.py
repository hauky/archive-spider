# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TSpiderConf(models.Model):
    spiderId = models.IntegerField(db_column='spiderId')  # Field name made lowercase.
    domain = models.CharField(max_length=255)
    sleepTime = models.IntegerField(db_column='sleepTime', blank=True, null=True)  # Field name made lowercase.
    listUrl = models.CharField(db_column='listUrl', max_length=255, blank=True, null=True)  # Field name made lowercase.
    detailUrl = models.CharField(db_column='detailUrl', max_length=255, blank=True, null=True)  # Field name made lowercase.
    titleXpath = models.CharField(db_column='titleXpath', max_length=255, blank=True, null=True)  # Field name made lowercase.
    timeXpath = models.CharField(db_column='timeXpath', max_length=255, blank=True, null=True)  # Field name made lowercase.
    authorXpath = models.CharField(db_column='authorXpath', max_length=255, blank=True, null=True)  # Field name made lowercase.
    contentXpath = models.TextField(db_column='contentXpath', blank=True, null=True)  # Field name made lowercase.
    createTime = models.DateTimeField(db_column='createTime', auto_now_add=True, max_length=0)  # Field name made lowercase.
    lastupdateTime = models.DateTimeField(db_column='lastUpdateTime', blank=True, null=True, auto_now_add=True, max_length=0)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 't_spider_conf'


class TSpiderResult(models.Model):
    confId = models.IntegerField(db_column='confId')  # Field name made lowercase.
    type = models.CharField(max_length=16)
    url = models.CharField(max_length=500)
    htmlContent = models.TextField(db_column='htmlContent')  # Field name made lowercase.
    htmlPath = models.CharField(db_column='htmlPath', max_length=128, blank=True, null=True)  # Field name made lowercase.
    pdfPath = models.CharField(db_column='pdfPath', max_length=128, blank=True, null=True)  # Field name made lowercase.
    createTime = models.DateTimeField(db_column='createTime', auto_now_add=True, max_length=0)  # Field name made lowercase.
    title = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=32, blank=True, null=True)
    time = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 't_spider_result'


class TSpiderTask(models.Model):
    name = models.CharField(max_length=32)
    cronExpression = models.CharField(db_column='cronExpression', max_length=32)  # Field name made lowercase.
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(default=0)
    delFlag = models.IntegerField(db_column='delFlag', blank=True, null=True)  # Field name made lowercase.
    creator = models.IntegerField(blank=True, null=True)
    createTime = models.DateTimeField(db_column='createTime', auto_now_add=True, max_length=0)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 't_spider_task'
