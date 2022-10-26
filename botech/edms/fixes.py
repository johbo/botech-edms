from django.shortcuts import get_object_or_404

from mayan.apps.metadata.models import DocumentMetadata, MetadataType


# TODO: Fix this upstream in mayan.apps.metadata.api
def save_metadata(metadata_dict, document, create=False, _user=None):
    """
    Take a dictionary of metadata type & value and associate it to a
    document
    """
    parameters = {
        'document': document,
        'metadata_type': get_object_or_404(
            klass=MetadataType, pk=metadata_dict['metadata_type_id']
        )
    }

    if create:
        # Use matched metadata now to create document metadata.
        try:
            document_metadata = DocumentMetadata.objects.get(**parameters)
        except DocumentMetadata.DoesNotExist:
            document_metadata = DocumentMetadata(**parameters)
            document_metadata._event_actior = _user
            document_metadata.save()
    else:
        try:
            document_metadata = DocumentMetadata.objects.get(
                document=document,
                metadata_type=get_object_or_404(
                    klass=MetadataType, pk=metadata_dict['metadata_type_id']
                ),
            )
        except DocumentMetadata.DoesNotExist:
            document_metadata = None

    if document_metadata:
        document_metadata.value = metadata_dict['value']
        document_metadata._event_actor = _user
        document_metadata.save()
