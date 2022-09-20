CODES_TO_RESEND = ['400', '403', '407', '500', '502', '503', '504', '523', '524']
URLS_TO_RESEND = [
    '/edo/maildoc_extinc_esedo/',
    '/edo/maildoc_extinc_esedo/?is_doc_appeal=true',
    '/edo/maildoc_extinc_esedo/?is_doc_section=true',
    '/edo/maildoc_extinc_esedo/?is_doc_ol=true',

    '/edo/receipt/?state_type=StateRegistered',
    '/edo/receipt/?state_type=StateDelivered',
    '/edo/receipt/?state_type=StateNotValid',
    '/edo/receipt/?state_type=StateExecution',
    '/edo/receipt/?state_type=StateFinished',
    '/edo/receipt/?state_type=startProcessResponse'
]
LOG_LOCATION = '/log'
