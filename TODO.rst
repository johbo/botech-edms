
======
 TODO
======

- [ ] docker image which contains the botech package
  - [x] put repository into Github -> easy download
  - [x] adapt docker file to install the python package
  - [x] push to imac via terraform as test-edms
  - [x] adapt settings
    So far only the following line was needed:
    "MAYAN_COMMON_EXTRA_APPS={botech.edms}",
  - [x] test
    Need one round of tweaks before using this.
  - [x] create needed matadata type configuration
  - [ ] test again after tweaking
    - [x] seems that the font is not included in the package, see manifest
  - [ ] update both edms systems
    - [ ] create missing metadata type entries in the botech system
  - [ ] app only active in the botech system, not in the private one

- [ ] Case "Already booked" to be improved. At the moment it does just raise an
  exception. A better interim solution would be to show an error message to the
  user. This way the user would still have access into the navigation.

- [ ] Improve handling of document type
      A link might be sufficient. When using "Actions -> Change Type" I am
      redirected back after storing the new type.
  - [ ] Adapt form, show type, date and optional description
  - [ ] Allow to update the type (?) Could also be via action with link back to
        the same page.

- [ ] Transformations
  - [ ] Store position information into attributes so that it is possible to
    manually adjust them for corner cases.

- [ ] Required metadata which does not yet have a value in the database causes
  the form to fail even though there are sensible default values provided. This
  should be improved.

- [ ] Add documentation as a Sphinx based document

- [ ] Add event into the audit log about usage of accounting view

- [ ] check if file cache can be invalidated when metadata changes so that the
  transformation is applied again.

- [ ] Handling of missing metadata in transformation

- [ ] Handling of the default value for the booked date.
  Just "date.today().isoformat()" may be a bit too naive.


- [ ] Document metadata configuration in handbook

- [ ] Send patch for "PageModel.parent" as a property or a utility method
      Replaces transformations._document_from_file_or_version_page

      See also the signature capture transformation which does implement a
      "get_document" as well. It also contains an if statement to differentiate
      between the page models. Think this knowledge should not be there.



- [ ] review permission handling
  - [ ] maybe introduce a specific permission for this form, since it does
        combine quite a few object types.

- [ ] create metadata configuration in dev system. test terraform provider.


- [ ] refactor

        # TODO: This is a copy from matadata.document_views, check if
        # redundancy in code can be avoided somehow.

- [ ] Menu Entry "Accounting" for documents in sub navigation would be nice.

- [ ] install ipdb into dev environment container

- [ ] special tag handling
    - if already tagged, show at least a warning
    - what happens if already tagged and the form is submitted

- [ ] Investigate how testing can be best applied
  - [ ] Simple unit testing which can be quickly used during development
  - [ ] A higher level testing method for checking the high level workflows and
        assumptions

- [ ] Investigate how to disable file caches for development

- [x] Add an accounting decoration to show accounting related information
      like a stamp on the document. This might be doable when using the decorations or
      transformations feature.
  - [x] Research how Decorations work

    Docs: Transformations are mentioned there, but not decorations.

    Transformations can both be applied to file pages as well as version pages.
    So a decision would have to be made, where it should be applied. Current
    thought is that we should go for the version and not for the file. Reason is
    that a file may also contain garbage from scanning. A version would be the
    view into the file and may have e.g. blank pages removed. Assumption is that
    the preview of a document also is based on the active version.

    The release notes of version 3.5 mention this, see
    https://docs.mayan-edms.com/releases/3.5.html?highlight=decorations#converter

    So it seems that this is based on transformations and just a new class or
    type of transformation.

    The implementation seems to be within the app "converter".

    There are two layers implemented: One is decorations and one is
    transformations, both seem to technically contain the same type of items.

    The transformations are registered into the layer, code is in the end of the
    file "transformations.py".

    The image manipulation code is inside of PIL.

  - [x] Add a custom decoration type
    - [x] register in layer
  - [x] Show "Booked"
  - [x] Find document in transformation

    converter.models contains LayerTransformation. This model configures a
    transformation for a given object. It is connected via a generic foreign key
    relation.

    Using "LayerTransformation.get_relation_class" is probably used to get the
    corresponding transformation.

    "LayerTransformatinManager" is providing a method "get_for_object" which
    does allow to get a list of instances of the transformation classes. Those
    instances seem to receive an attribute "object_layer":

        tranformation_instance.object_layer = transformation.object_layer

    This is an instance of the model "ObjectLayer" which contains the
    relationship to the original object:

        content_type = models.ForeignKey(on_delete=models.CASCADE, to=ContentType)
        object_id = models.PositiveIntegerField()
        content_object = GenericForeignKey(
            ct_field='content_type', fk_field='object_id'
        )

    If this attribute is present on the running transformation, then this allows
    to find the document with ease and get all required data.

    The app "signature_capture" is using this attribute, so it seems to be
    intended for this purpose.

  - [x] placement from the right side
  - [x] test if opacity can be added
  - [x] Show document number
  - [x] Show date "Booked 2022-08-25"
        This means that the date will have to be tracked, could be a custom metadata type.
  - [x] Show the accounting comment
        This means that the accounting comment will become special, so this should
        be captured in a metadata attribute.
  - [x] Refactor: Names of metadata types into literals.py
  - [x] Refactor: Track the comment in a metadata field
    - [x] show initial value if present
    - [x] hide comment from metadata overview
  - [x] Refactor: Track the date in a metadata field and set it on submit
  - [x] Automatically create a new version with the decorations attached on
        submit. Think twice, does it really need a new version? Just add the
        decoration to the active version.

        Conclusion is to automatically attach it to the active version.
  - [x] Ensure that the file cache is invalidated


- [x] Tag attachment is missing the correct user in the event. Probably some
      context has to be provided.
      The instance can be assigned an attribute "_event_actor" to inject this
      information.
- [x] Only attach tag if it is not yet attached

- [x] Only change Metadata if the value did change. Avoids that events are
      triggered.
      It might already work if there is a way to avoid that the "Update" flags are
      checked by default.
      - [x] Investigate the Metadata view used via "Actions -> Edit Metadata"
            It seems to suffer the same issue.
      - [x] Investigate the Form and view implementation
            The attribute "update" is configured with "initial=True".
            It seems tat the view will have to pass in values for "initial".
      - [x] Set "initial" in view
            This does make the form validation fail, still, why should it fail if I
            don't want to change a value even if it is required?
      - [x] Find out why form validation fails.


- [x] Register document action
  - [x] link
  - [x] view?
  - [x] register url
  - [x] link to menu

- [x] Add custom view

  Used a copy of the confirmation view when trashing a document.

- [x] Simple form to update metadata
  - [x] MultiFormView
  - [x] Make view work, even if empty
  - [x] add debug_toolbar, add into middleware This did prove to be totally
    useless in the first attempt. It did clash with the UI JS black magic and I
    had no access into the relevant request context information.
  - [x] Display MetaDataForm - this failed, tricky to debug in the current
    setup, doing a proper dev setup on the local machine. Then back to this one.
    - [x] parameter "subtemplates_list" in template context missing. This is the
      reason why nothing is visible.
    - [x] metadata items visible


- [x] dev env setup
  - [x] study manual to find the guide
    https://docs.mayan-edms.com/chapters/development/development_deployment.html
  - [x] test local docker setup
    Flawless
  - [x] study if there are alternatives
    QEMU seems to be promising, can be installed without
    trouble via Nix, test later if Docker does not work as expected.
  - [x] use a ubuntu base image to start from
    Used the debian image which the edms repository also uses
  - [x] check if either terraform or docker-compose can help to have a dev-image
    easily available and run commands
    docker compose is the way to go.
  - [x] move repositories over to local machine
  - [x] runserver in dev-env image
  - [x] botech-edms in dev-install included
  - [x] back to the display of the form data
  - [x] test initialize

- [x] store change on document metadata on submit
  - [x] hide other forms
  - [x] form display mode parameter into context
  - [x] add second metadata field
  - [x] store data

    def form_valid(self, form):
        self.view_action(form=form)
        return super().form_valid(form=form)

    have to implement "all_forms_valid" or better "form_valid__FORMNAME"

    ! second form seems to have a bug in the implementation, use first variant!

  - [x] handle issues
    This did work out of the box.

- [x] fix up style of metadata display. Should look like the other places.
  Parameter in the context for tabular display.

- [x] success and failure message into view

- [x] Cancel Button
  Did appear automatically

- [x] actions and sub-navigation missing in display of the form

  Note: This may actually be an advantage, still, should find out why this is
  and how this can be influenced.

  It became visible once I did change the view to the single object view. This
  also does make sense since the sub navigation is related to a specific
  document. A view which would allow to handle multiple documents could not
  reasonably show this many.

- [x] display actual data in the forms

- [x] show document type
  - [x] Use the properties display
  - [x] research django forms, multiple forms in one post

    Django does use the "prefix" so that multiple forms can be put into one
    "FORM" tag.

    Now it's a matter of the right templates. Might be that custom adaptions are
    needed to the EDMS templates.
  - [x] Verify templates

    "generic_form" is the entry point. It can dispatch to "form_subtemplate" if
    a single form is in the context. And it can dispatch into a list of
    "subtemplates".

    "generic_form_instance" does render the inner things inside a FORM tag.

    "generic_form_subtemplate" does render the FORM tag and then dispatch into
    "form_instance".

    "generic_multiform_subtemplate" does render the FORM tag and then iterate
    over "forms". Per form it does dispatch to "form_instance".

    Conclusions:

    - generic form subtemplate without FORM tag
    - generic form which wraps subtemplates in FORM tag
    - one set of submit / cancel buttons in generic template
  - [x] don't fail on read only forms
  - [x] render form into one multi form

- [x] show a comment field
  - [x] show the comment field
  - [x] create a comment on the document if text is present
  - [x] compare model form, to check who should create

    Django's model form does create the model instance and store it. In this
    simple case the code stays in the view. Complex cases should either go into
    the form or a separate class.

- [x] tag on submit
  - [x] inspect tag model
    The setting must contain the tag label.
  - [x] settings regarding Tag Label
  - [x] tag handling

- [x] require acct_doc_number on submit
  - [x] show field always in form
  - [x] require a value
  - [x] setting regarding name

- [x] Allow to add metadata items which are not yet in the database.

  E.g. document number may not yet be set, the form should always show it and
  instead of only updating if it does already exist in the database, it should
  create a new item.

- [x] show a preview of the document

- [x] Investigate what interactive transformations in doc version page model are
      Try to find out what the intended usage is.

      Did not find a good starting point, and it's not that important anymore.
