import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template import loader
from django.http import HttpResponse
# Create your views here.


class address:
    def __init__(self, kor_addr, eng_addr, zip_code):
        self.kor = kor_addr
        self.eng = eng_addr
        self.zip = zip_code
        if self.eng.split(', ')[-1].endswith('-do'):
            self.state= self.eng.split(', ')[-1]
            self.city= self.eng.split(', ')[-2]
        else:
            self.state = self.eng.split(', ')[-1]
            self.city = self.eng.split(', ')[-1]


class searched_address:
    '''
      잘못된 검색어가 검색되어 findAll 결과가 none이 될 경우 어떻게 할지..고민..
    '''
    def __init__(self, addr):
        # 최대 10 page 출력
        self.urls = ["https://www.juso.go.kr/addrlink/addrLinkApi.do?currentPage="+str(x)+"&countPerPage=100%20&keyword=" + addr + "&confmKey=U01TX0FVVEgyMDIxMDMyODE0MzE1MjExMDk3NDc=&firstSort=road" for x in range(1,11)]
        self.htmls = []
        for i in range(10):
            html = BeautifulSoup(requests.get(self.urls[i]).content, 'xml')
            if int(html.find('totalCount').text)==0:
                break
            self.htmls.append(html)


    def get_addr_list(self):
        kor_list = []
        eng_list = []
        zip_list = []
        for html in self.htmls:
            kor_list += html.findAll('roadAddr')
            eng_list += html.findAll('engAddr')
            zip_list += html.findAll('zipNo')
        addr_list = []
        if kor_list:
            for i in range(len(zip_list)):
                new_address = address(kor_list[i].text, eng_list[i].text, zip_list[i].text)
                addr_list.append(new_address)
        return addr_list


def home(request):
    context = {'home_name':'영문주소변환'}
    return render(request, 'kor2eng/home.html', context)


def search_result(request):
    kor_addr = request.GET.get('q')
    result = searched_address(kor_addr)
    '''
    eng_addr = html.find('engAddr').text
    zip_code = html.find('zipNo').text
    city, state = address_parse(eng_addr)
    if eng_addr==None:
        eng_addr = '잘못된 주소입니다'
    '''
    result_list = result.get_addr_list()
    paginator = Paginator(result_list, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {'posts':posts, 'q':kor_addr}
    return render(request, 'kor2eng/search_results.html', context)


def detail_address(request, kor_add):
    kor_addr = kor_add
    url = "https://www.juso.go.kr/addrlink/addrLinkApi.do?currentPage=1&countPerPage=10%20&keyword=" + kor_addr + "&confmKey=U01TX0FVVEgyMDIxMDMyODE0MzE1MjExMDk3NDc=&firstSort=road"
    html = BeautifulSoup(requests.get(url).content, 'xml')
    print(html)
    eng = html.find('engAddr').text
    zip = html.find('zipNo').text
    kor = html.find('roadAddr').text
    addr = address(kor, eng, zip)
    context = {"addr" : addr}
    return render(request, 'kor2eng/detail_address.html', context)



