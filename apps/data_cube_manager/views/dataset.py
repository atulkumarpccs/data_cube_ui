from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from django.conf import settings
from django.views import View

from urllib import parse
from collections import OrderedDict

from . import models
from . import forms


class DatasetListView(View):
    """View datasets with a filtering form

    Enumerate all datasets that fit the entered criteria using Data Tables server side processing

    """

    def get(self, request, dataset_type_id=None):
        """Display the rendered HTML datatables instance and form.

        If dataset_type_id is not none, use it to initialize the form.

        Context:
            form: DatasetFilerForm instance, bound to dataset_type_id if available
        """
        context = {
            'form': forms.DatasetFilterForm({
                'dataset_type_ref': [dataset_type_id] if dataset_type_id is not None else [1]
            })
        }
        return render(request, 'data_cube_manager/datasets.html', context)

    def post(self, request, dataset_type_id=None):
        """Acts as the server process for DataTables.

        Uses the DataTables request details to return the required DT response.
        See https://datatables.net/manual/server-side for more details.

        """
        form_data = parse.parse_qs(request.POST['form_data'])
        # unlist the post data - data tables uses lists for everything for w/e reason.
        for key in form_data:
            if "dataset_type_ref" == key:
                continue
            form_data[key] = form_data[key][0]

        dataset_filters = forms.DatasetFilterForm(form_data)
        if dataset_filters.is_valid():
            ending_slice = int(request.POST.get('start')) + int(
                request.POST.get('length')) if request.POST.get('length') != "-1" else -1
            datasets = models.Dataset.filter_datasets(dataset_filters.cleaned_data)
            total_records = datasets.count()

            order_dir = "-" if request.POST.get("order[0][dir]") == "desc" else ""
            order_col = request.POST.get("columns[{}][name]".format(request.POST.get("order[0][column]")[0]))

            sliced_datasets = datasets.order_by(
                "{}{}".format(order_dir, order_col))[int(request.POST.get('start')):ending_slice]

            data = [dataset.get_dataset_table_columns() for dataset in sliced_datasets]
            context = {
                'draw': int(request.POST.get('draw')),
                'recordsTotal': total_records,
                'recordsFiltered': total_records,
                'data': data,
            }
            return JsonResponse(context)
        else:
            for error in dataset_filters.errors:
                context = {'draw': int(request.POST.get('draw')), 'data': [], 'error': dataset_filters.errors[error]}
                return JsonResponse(context)


class DeleteDataset(View):
    """Delete datasets using some filtering criteria provided by a form"""

    def get(self, request):
        """Get a Json response describing what will be deleted

        GET data:
            Bound DatasetFilterForm used to select datasets for removal

        Returns:
            Json response with either an error message or the number of datasets that will be removed
        """
        if not request.user.is_superuser:
            return JsonResponse({'status': "ERROR", 'message': "Only superusers can delete datasets."})

        dataset_filters = forms.DatasetFilterForm(request.GET)
        if dataset_filters.is_valid():
            datasets = models.Dataset.filter_datasets(dataset_filters.cleaned_data)
            total_records = datasets.count()
            total_datasets = len(dataset_filters.cleaned_data.get('dataset_type_ref'))

            context = {
                'status': "OK",
                'total_records': total_records,
                'total_dataset_types': total_datasets,
            }
            return JsonResponse(context)
        else:
            for error in dataset_filters.errors:
                context = {'status': "ERROR", 'message': dataset_filters.errors[error]}
                return JsonResponse(context)

    def post(self, request):
        """Delete datasets based on a DatasetFilterForm

        POST data:
            Bound DatasetFilterForm used to select datasets for removal

        """
        if not request.user.is_superuser:
            return JsonResponse({'status': "ERROR", 'message': "Only superusers can delete datasets."})
        dataset_filters = forms.DatasetFilterForm(request.POST)
        if dataset_filters.is_valid():
            filtered_datasets = models.Dataset.filter_datasets(dataset_filters.cleaned_data)
            filtered_datasets.delete()
            context = {'status': "OK"}
            return JsonResponse(context)
        else:
            for error in dataset_filters.errors:
                context = {'status': "ERROR", 'message': dataset_filters.errors[error]}
                return JsonResponse(context)
