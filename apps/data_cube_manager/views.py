from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from django.conf import settings
from django.views import View

import os
import yaml
from yaml import SafeDumper
import uuid
from datacube.index import index_connect

from . import models
from . import forms
from . import utils

import json


class DatasetTypeListView(View):
    """Main end point for viewing the list of active dataset types"""

    def get(self, request):
        """
        """
        context = {}
        context['dataset_types'] = models.DatasetType.objects.using('agdc').all()
        return render(request, 'data_cube_manager/view_dataset_types.html', context)


class DatasetTypeView(View):
    """Main end piont for viewing or adding a dataset type"""

    def get(self, request):
        """
        """
        context = {
            'measurements_form': forms.DatasetTypeMeasurementsForm(),
            'flags_definition_form': forms.DatasetTypeFlagsDefinitionForm(),
            'spectral_definition_form': forms.DatasetTypeSpectralDefinitionForm(),
            'dataset_type_id': dataset_type_id
        }
        dataset_type = models.DatasetType.objects.using('agdc').get(id=dataset_type_id)
        context.update(utils.forms_from_definition(dataset_type.definition, display_only=True))
        #def includes metadata.
        return render(request, 'data_cube_manager/add_dataset_type.html', context)

    def post(self, request):
        """
        """
        context = {
            'measurements_form': forms.DatasetTypeMeasurementsForm(),
            'flags_definition_form': forms.DatasetTypeFlagsDefinitionForm(),
            'spectral_definition_form': forms.DatasetTypeSpectralDefinitionForm(),
        }
        if dataset_type_id:
            dataset_type = models.DatasetType.objects.using('agdc').get(id=dataset_type_id)
            context.update(utils.forms_from_definition(dataset_type.definition, display_only=False))
        else:
            context['metadata_form'] = forms.DatasetTypeMetadataForm()
        return render(request, 'data_cube_manager/add_dataset_type.html', context)


class CreateDatasetType(View):
    """"""

    def get(self, request):
        """
        """
        if not request.method == 'POST':
            return JsonResponse({'error': "ERROR", 'msg': "Only POST data is allowed."})
        form_data = request.POST
        measurements = json.loads(form_data.get('measurements'))
        metadata = json.loads(form_data.get('metadata_form'))
        #each measurement_form contains a dict of other forms..
        measurement_forms = [utils.create_measurement_form(measurements[measurement]) for measurement in measurements]
        #just a single form
        metadata_form = utils.create_metadata_form(metadata)

        for measurement_form_group in measurement_forms:
            for form in filter(lambda x: not measurement_form_group[x].is_valid(), measurement_form_group):
                for error in measurement_form_group[form].errors:
                    return JsonResponse({'error': "ERROR", 'msg': measurement_form_group[form].errors[error][0]})
        if not metadata_form.is_valid():
            for error in metadata_form.errors:
                return JsonResponse({'error': "ERROR", 'msg': metadata_form.errors[error][0]})

        #since everything is valid, now create yaml from defs..
        product_def = utils.definition_from_forms(metadata_form, measurement_forms)
        try:
            os.makedirs('/datacube/ui_results/data_cube_manager/product_defs/')
        except:
            pass
        yaml_url = '/datacube/ui_results/data_cube_manager/product_defs/' + str(uuid.uuid4()) + '.yaml'
        with open(yaml_url, 'w') as yaml_file:
            yaml.dump(dict(product_def), yaml_file, Dumper=SafeDumper)
        return JsonResponse({'error': 'OK', 'url': yaml_url})

    def post(self, request):
        """"""
        if not request.user.is_superuser:
            return JsonResponse({'error': "ERROR", 'msg': "Only superusers can add or update datasets."})

        form_data = request.POST
        measurements = json.loads(form_data.get('measurements'))
        metadata = json.loads(form_data.get('metadata_form'))
        #each measurement_form contains a dict of other forms..
        measurement_forms = [utils.create_measurement_form(measurements[measurement]) for measurement in measurements]
        #just a single form
        metadata_form = utils.create_metadata_form(metadata)

        for measurement_form_group in measurement_forms:
            for form in filter(lambda x: not measurement_form_group[x].is_valid(), measurement_form_group):
                for error in measurement_form_group[form].errors:
                    return JsonResponse({'error': "ERROR", 'msg': measurement_form_group[form].errors[error][0]})
        if not metadata_form.is_valid():
            for error in metadata_form.errors:
                return JsonResponse({'error': "ERROR", 'msg': metadata_form.errors[error][0]})

        if models.DatasetType.objects.using('agdc').filter(name=metadata_form.cleaned_data['name']).exists():
            return JsonResponse({
                'error':
                "ERROR",
                'msg':
                'A dataset type already exists with the entered name. Please enter a new name for your dataset and ensure that the definition is different.'
            })

        #since everything is valid, now create yaml from defs..
        product_def = utils.definition_from_forms(metadata_form, measurement_forms)

        index = index_connect()
        try:
            type_ = index.products.from_doc(product_def)
            index.products.add(type_)
        except:
            return JsonResponse({
                'error':
                "ERROR",
                'msg':
                'Invalid product definition. Please contact a system administrator if this problem persists.'
            })

        return JsonResponse({'error': 'ok', 'msg': 'Your dataset type has been added to the database.'})


class DeleteDatasetType(View):

    def get(self, request):
        """Get the datasets that will be deleted/confgirmation?"""

    def post(self, request):
        """Delete the type"""


class DatasetListView(View):
    """
    """

    def get(self, request):
        """
        """
        context = {}
        context['datasets'] = models.Dataset.objects.using('agdc').filter(dataset_type_ref=dataset_type_ref)
        context['downloadable'] = 'managed' in models.DatasetType.objects.using('agdc').get(
            id=dataset_type_ref).definition
        return render(request, 'data_cube_manager/view_datasets.html', context)

    def post(self, request):
        """
        """
        location = models.DatasetLocation.objects.using('agdc').get(dataset_ref=dataset_ref)
        return redirect(settings.BASE_HOST + location.uri_body.strip("/"))


class DeleteDataset(View):
    """
    """

    def get(self, request):
        """
        """

    def post(self, request):
        """
        """


def validate_measurement(request):
    if not request.method == 'POST':
        return JsonResponse({'error': "ERROR", 'msg': "Only POST data is allowed."})
    form_data = request.POST
    measurement_forms = utils.create_measurement_form(form_data)
    #filters out all valid forms.
    for form in filter(lambda x: not measurement_forms[x].is_valid(), measurement_forms):
        for error in measurement_forms[form].errors:
            return JsonResponse({'error': "ERROR", 'msg': measurement_forms[form].errors[error][0]})
    return JsonResponse({'error': "OK", 'msg': "OK"})
