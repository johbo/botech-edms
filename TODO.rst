
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

- [ ] store change on document metadata on submit
  - [x] hide other forms
  - [x] form display mode parameter into context
  - [x] add second metadata field
  - [ ] store data

    def form_valid(self, form):
        self.view_action(form=form)
        return super().form_valid(form=form)

    have to implement "all_forms_valid" or better "form_valid__FORMNAME"

    ! second form seems to have a bug in the implementation, use first variant!

  - [ ] handle issues

- [ ] fix up style of metadata display. Should look like the other places.

- [ ] actions and sub-navigation missing in display of the form

- [ ] display actual data in the forms

- [ ] success and failure message into view

- [ ] Cancel Button

- [ ] show a preview of the document

- [ ] show a comment field

- [ ] show document type

- [ ] tag on submit

- [ ] require acct_doc_number on submit

- [ ] create metadata configuration in dev system. test terraform provider.
