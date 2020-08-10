from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
from django.http.request import QueryDict
import json

from .models import TSpiderTask, TSpiderConf, TSpiderResult
# Create your views here.


@require_http_methods(["POST"])
def add_tasks(request):
    response = {}
    try:
        response['message'] = 'success'
        response['status'] = 0

        name = request.POST.get('name')
        cronExpression = request.POST.get('cronExpression')
        description = request.POST.get('description')
        status = request.POST.get('status')
        delFlag = request.POST.get('delFlag')
        creator = request.POST.get('creator')

        TSpiderTask.objects.create(name=name, cronExpression=cronExpression, description=description,
                                   status=status, delFlag=delFlag, creator=creator)
    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["POST"])
def add_confs(request):
    response = {}
    try:
        response['message'] = 'success'
        response['status'] = 0

        spiderId = request.POST.get('spiderId')
        domain = request.POST.get('domain')
        sleepTime = request.POST.get('sleepTime')
        listUrl = request.POST.get('listUrl')
        detailUrl = request.POST.get('detailUrl')
        titleXpath = request.POST.get('titleXpath')
        timeXpath = request.POST.get('timeXpath')
        authorXpath = request.POST.get('authorXpath')
        contentXpath = request.POST.get('contentXpath')

        TSpiderConf.objects.create(spiderId=spiderId, domain=domain, sleepTime=sleepTime, listUrl=listUrl,
                                   detailUrl=detailUrl, titleXpath=titleXpath, timeXpath=timeXpath,
                                   authorXpath=authorXpath, contentXpath=contentXpath)

    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["POST"])
def add_results(request):
    response = {}
    try:
        response['message'] = 'success'
        response['status'] = 0

        confId = request.POST.get('confId')
        type = request.POST.get('type')
        url = request.POST.get('url')
        htmlContent = request.POST.get('htmlContent')
        htmlPath = request.POST.get('htmlPath')
        pdfPath = request.POST.get('pdfPath')
        module = request.POST.get('module')
        title = request.POST.get('title')
        author =request.POST.get('author')
        time = request.POST.get('time')

        TSpiderResult.objects.create(confId=confId, type=type, url=url, htmlContent=htmlContent, htmlPath=htmlPath,
                                     pdfPath=pdfPath, module=module, title=title, author=author, time=time)

    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["POST"])
def delete_tasks(request):
    # 根据POST请求里包含的爬虫任务名来删除数据
    response = {}
    try:
        response['message'] = 'success'
        response['status'] = 0

        name = request.POST.get('name')
        TSpiderTask.objects.filter(name=name).delete()

    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)

    return JsonResponse(response)


@require_http_methods(["POST"])
def delete_confs(request):
    # 根据POST请求里包含的domain来删除数据
    response = {}
    try:
        response['message'] = 'success'
        response['status'] = 0

        domain = request.POST.get('domain')
        TSpiderConf.objects.filter(domain=domain).delete()

    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)

    return JsonResponse(response)


@require_http_methods(["POST"])
def delete_results(request):
    # 根据POST请求里包含的时间条件来删除数据
    # 大于/小于/等于 这个时间的记录删掉
    # 时间格式可以为日期：2020-08-05 也可以为具体时间：2020-08-05 17:10:08
    response = {}
    try:
        response['message'] = 'success'
        response['status'] = 0

        createTime = request.POST.get('createTime')
        # __gte 大于等于
        TSpiderResult.objects.filter(createTime__gte=createTime).delete()

    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)

    return JsonResponse(response)


@require_http_methods(["POST"])
def modify_tasks(request):
    # 根据id来查找记录
    response = {}
    try:
        response['message'] = 'success'
        response['status'] = 0

        id = request.POST.get('id')
        name = request.POST.get('name')
        cronExpression = request.POST.get('cronExpression')
        description = request.POST.get('description')
        status = request.POST.get('status')
        delFlag = request.POST.get('delFlag')
        creator = request.POST.get('creator')

        TSpiderTask.objects.filter(id=id).update(name=name, cronExpression=cronExpression, description=description,
                                   status=status, delFlag=delFlag, creator=creator)
    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["POST"])
def modify_confs(request):
    # 根据id来查找记录
    response = {}
    try:
        response['message'] = 'success'
        response['status'] = 0

        id = request.POST.get('id')
        spiderId = request.POST.get('spiderId')
        domain = request.POST.get('domain')
        sleepTime = request.POST.get('sleepTime')
        listUrl = request.POST.get('listUrl')
        detailUrl = request.POST.get('detailUrl')
        titleXpath = request.POST.get('titleXpath')
        timeXpath = request.POST.get('timeXpath')
        authorXpath = request.POST.get('authorXpath')
        contentXpath = request.POST.get('contentXpath')

        TSpiderConf.objects.filter(id=id).update(spiderId=spiderId, domain=domain, sleepTime=sleepTime, listUrl=listUrl,
                                   detailUrl=detailUrl, titleXpath=titleXpath, timeXpath=timeXpath,
                                   authorXpath=authorXpath, contentXpath=contentXpath)

    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["POST"])
def modify_results(request):
    # 根据id来查找记录
    response = {}
    try:
        response['message'] = 'success'
        response['status'] = 0

        id = request.POST.get('id')
        confId = request.POST.get('confId')
        type = request.POST.get('type')
        url = request.POST.get('url')
        htmlContent = request.POST.get('htmlContent')
        htmlPath = request.POST.get('htmlPath')
        pdfPath = request.POST.get('pdfPath')
        module = request.POST.get('module')
        title = request.POST.get('title')
        author = request.POST.get('author')
        time = request.POST.get('time')

        TSpiderResult.objects.filter(id=id).update(confId=confId, type=type, url=url, htmlContent=htmlContent,
                                                   htmlPath=htmlPath, pdfPath=pdfPath, module=module,
                                                   title=title, author=author, time=time)

    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)

@require_http_methods(["POST"])
def show_tasks(request):
    # 根据id来查找并展示记录
    response = dict()
    try:
        id = request.POST.get('id')
        tasks = TSpiderTask.objects.filter(id=id).all()
        response['message'] = 'success'
        response['status'] = 0

        response['data'] = []
        temp_list = json.loads(serializers.serialize("json", tasks))
        for each_dict in temp_list:
            response['data'].append(each_dict['fields'])
    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["POST"])
def show_confs(request):
    # 根据id来查找并展示记录
    response = dict()
    try:
        id = request.POST.get('id')
        confs = TSpiderConf.objects.filter(id=id).all()
        response['message'] = 'success'
        response['status'] = 0

        response['data'] = []
        temp_list = json.loads(serializers.serialize("json", confs))
        for each_dict in temp_list:
            response['data'].append(each_dict['fields'])
    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["POST"])
def show_results(request):
    # 根据id来查找并展示记录
    response = dict()
    try:
        id = request.POST.get('id')
        results = TSpiderResult.objects.filter(id=id).all()
        response['message'] = 'success'
        response['status'] = 0

        response['data'] = []
        temp_list = json.loads(serializers.serialize("json", results))
        for each_dict in temp_list:
            response['data'].append(each_dict['fields'])
    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["GET"])
def show_all_tasks(request):
    response = dict()
    try:
        tasks = TSpiderTask.objects.all()
        response['message'] = 'success'
        response['status'] = 0

        response['data'] = []
        temp_list = json.loads(serializers.serialize("json", tasks))
        for each_dict in temp_list:
            response['data'].append(each_dict['fields'])
    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["GET"])
def show_all_confs(request):
    response = dict()
    try:
        confs = TSpiderConf.objects.all()
        response['message'] = 'success'
        response['status'] = 0

        response['data'] = []
        temp_list = json.loads(serializers.serialize("json", confs))
        for each_dict in temp_list:
            response['data'].append(each_dict['fields'])
    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)


@require_http_methods(["GET"])
def show_all_results(request):
    response = dict()
    try:
        results = TSpiderResult.objects.all()
        response['message'] = 'success'
        response['status'] = 0

        response['data'] = []
        temp_list = json.loads(serializers.serialize("json", results))
        for each_dict in temp_list:
            response['data'].append(each_dict['fields'])
    except Exception as e:
        response['status'] = -1
        response['message'] = str(e)
    return JsonResponse(response)
