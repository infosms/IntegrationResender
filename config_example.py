#TYPES_TO_RESEND = ['docOutgoing', 'docAppeal', 'docSection', '']
CODES_TO_RESEND = ['403', '500', '502', '503', '504']
URLS_TO_RESEND = [
    '/edo/maildoc_extinc_esedo/',
    '/edo/maildoc_extinc_esedo/?is_doc_appeal=true',
    '/edo/maildoc_extinc_esedo/?is_doc_section=true',
    '/edo/maildoc_extinc_esedo/?is_doc_ol=true',

    '/edo/receipt/?state_type=StateRegistered',
    #'/edo/receipt/?state_type=StateDelivered',
    #'/edo/receipt/?state_type=StateNotValid',
    #'/edo/receipt/?state_type=StateExecution',
    #'/edo/receipt/?state_type=StateFinished',
    #'/edo/receipt/?state_type=startProcessResponse'
]
