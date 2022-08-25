
======
 TODO
======


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

- [ ] Improve handling of document type
  - [ ] Adapt form, show type, date and optional description
  - [ ] Allow to update the type (?) Could also be via action with link back to
        the same page.

- [ ] create metadata configuration in dev system. test terraform provider.


- [ ] refactor

        # TODO: This is a copy from matadata.document_views, check if
        # redundancy in code can be avoided somehow.

- [ ] Menu Entry "Accounting" for documents in sub navigation would be nice.

- [ ] install ipdb into dev environment container

- [ ] special tag handling
    - if already tagged, show at least a warning
    - what happens if already tagged and the form is submitted
