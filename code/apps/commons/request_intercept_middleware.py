from django.shortcuts import redirect, render

def browser_check(get_response):

    def middleware(request):
        warning_flag = False
        if request.method == 'GET':
            if not request.user_agent.is_mobile:
                if 'redirect_flag' in request.session and request.session['redirect_flag']:
                    warning_flag = False
                    del request.session['redirect_flag']
                else:
                    warning_flag = True
        
        if warning_flag:     
            return render(request, 'online-store/browser_warning.html')
        else:
            response = get_response(request)
            if 300 <= response.status_code < 400:
                request.session['redirect_flag'] = True
            return response
                
    return middleware
    