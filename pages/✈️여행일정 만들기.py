import streamlit as st
from openai import OpenAI
import time
from PIL import Image
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import json


client = OpenAI(api_key = st.secrets['OPENAI_API_KEY'])

# ==============================================================================================================
st.title(' ')
st.title("AI 여행 계획 짜기")
st.subheader("🌎 어디로 떠나고 싶나요?")
st.title(' ')
# ==============================================================================================================
def generate_itinerary(country,city,nights,days,places,activities,etc):
    prompt = f'''
{country}의 {city}에서 {nights}박 {days}일 여행 일정표를 만들어주세요.
{places}도 포함해주세요.
{activities}도 포함해 주세요.
장소,활동,요리가 주어질 경우 반드시 포함해야 합니다.
{etc}가 주어질 경우 반드시 고려하여 작성해주세요.
마지막으로 {city}를 여행할 때 주의해야 될 사항을 3가지만 알려주세요.
---
국가 : {country}
도시 : {city}
일정 : {nights}박 {days}일
방문지 : {places}
활동 : {activities}
---    
    '''.strip()
    return prompt
# ==============================================================================================================
def request_chat_completion(prompt):
    response = client.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages = [
            {'role' : 'system', 'content' : '당신은 전문 여행계획가 입니다.'},
            {'role' : 'user', 'content' : prompt}
        ],
        stream = True
    )
    return response
# ==============================================================================================================
def print_streaming_response(response):
    message = ''
    placeholder = st.empty()
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            message += delta.content
            placeholder.markdown(message + "▌")
    placeholder.markdown(message)
# ==============================================================================================================
def information_crawling(country,city):
    url = f'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={country,city}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'html.parser')
    items = soup.select('.value-_R4Lp')
    image_urls = [img['src'] for img in soup.select('.img_list .item img')]
    
    columns = st.columns(2)
    for i,url in enumerate(image_urls):
        response = requests.get(url)
        if i % 2 == 0:
            columns[0].image(Image.open(BytesIO(response.content)),width=330)
        else:
            columns[1].image(Image.open(BytesIO(response.content)),width=330)
        if i == 1:
            break
    if not items:
        st.write('추천 : ', None)
        st.write('비행시간 : ', None)
        st.write('비자 : ',  None)
        st.write('환율 : ', None)
        st.write('전압 : ', None)
    for i,item in enumerate(items):
        text = item.get_text().strip()
        if i == 0:
            st.write('추천 : ', text)
        if i == 1:
            st.write('비행시간 : ', text)
        if i == 2:
            st.write('비자 : ', text)
        if i == 3:
            st.write('환율 : ', text )
        if i == 4:
            st.write('전압 : ', text)
# ==============================================================================================================
    

tab_itineary,tab_weather,tab_food,tab_hotel = st.tabs(['일정','날씨','음식','호텔'])

# =====================================================================================================

with tab_itineary:
    with st.form('form1'):
        st.text('아래의 정보를 입력하세요')
        col1,col2 = st.columns(2)
        with col1:
            country = st.text_input(
                '국가 (필수)'
            )
        with col2:
            city = st.text_input(
                '도시 (필수)'
            )
            
        col1,col2 = st.columns(2)
        with col1:
            nights = st.number_input(
                '0 박 (필수)',
                min_value = 0,
                max_value = 30,
                step = 1,
                value = 3
            )
        with col2:
            days = st.number_input(
                '0 일 (필수)',
                min_value = 1,
                max_value = 30,
                step = 1,
                value = 4
            )
        st.text('원하는 방문지를 입력하세요 (필수 아님)')
        col1,col2,col3 = st.columns(3)
        with col1:
            place_one = st.text_input(
                '방문지1'
            )
        with col2:
            place_two = st.text_input(
                '방문지2'
            )
        with col3:
            place_three = st.text_input(
                '방문지3'
            )
            
        st.text('원하는 활동을 입력하세요 (필수 아님)')
        col1,col2,col3 = st.columns(3)
        with col1:
            activity_one = st.text_input(
                '활동1'
            )
        with col2:
            activity_two = st.text_input(
                '활동2'
            )
        with col3:
            activity_three = st.text_input(
                '활동3'
            )
        etc = st.text_input(
            '원하는 사항이 있으면 입력하세요 (필수 아님)'
        )
        submit = st.form_submit_button('제출하기')  
              
        st.write('제출 후 잠시만 기다려주세요!')
        
        if submit:
            if not country:
                st.error('국가를 입력해주세요')
            elif not city:
                st.error('도시를 입력해주세요')
            else:
                places = [place_one,place_two,place_three]
                places = [x for x in places if x]
                activities = [activity_one,activity_two,activity_three]
                activities = [x for x in activities if x]
                etc = [x for x in etc if x]
                prompt = generate_itinerary(
                    country = country,
                    city = city,
                    nights = nights,
                    days = days,
                    places = places,
                    activities = activities,
                    etc = etc
                )
                response = request_chat_completion(prompt)
                information_crawling(country,city)
                st.write('======================================================================')
                print_streaming_response(response)

# ===========================================================================================

def generate_weather(country,city,month):
    prompt = f'''
{month}월에 {country}의 {city}를 여행할겁니다.
해당 {city}의 {month}월 날씨와 가져갈 옷을 추천해주세요.
'''.strip()
    return prompt
                
with tab_weather:
    with st.form('form2'):
        st.text("아래의 정보를 입력하세요")
        col1,col2,col3 = st.columns(3)
        with col1:
            country = st.text_input(
                '국가 (필수)'
            )
        with col2:
            city = st.text_input(
                '도시 (필수)'
            )
        with col3:
            month = st.number_input(
                '월 (필수)',
                min_value = 1,
                max_value = 12,
                step = 1,
                value = 1   
            )
        submit = st.form_submit_button('제출하기')
        st.write('제출 후 잠시만 기다려주세요!')
        if submit:
            if not country:
                st.error('국가를 입력해주세요')
            elif not city:
                st.error('도시를 입력해주세요')
            elif not month:
                st.error('월을 입력해주세요')
            else:
                prompt = generate_weather(
                    country = country,
                    city = city,
                    month = month
                )
                response = request_chat_completion(prompt)
                print_streaming_response(response)
                
# ======================================================================================================

def generate_food(country,city):
    prompt = f'''
{country}의 {city}를 여행할겁니다.
해당 {city}의 맛있는 요리 3가지 추천해주세요.
'''.strip()
    return prompt

with tab_food:
    with st.form('form3'):
        st.text('아래의 정보를 입력하세요')
        col1,col2 = st.columns(2)
        with col1:
            country = st.text_input(
                '국가 (필수)'
            )
        with col2:
            city = st.text_input(
                '도시 (필수)'
                
            )
        submit = st.form_submit_button('제출')
        st.write('제출 후 잠시만 기다려주세요!')
        if submit:
            if not country:
                st.error('국가를 입력해주세요')
            elif not city:
                st.error('도시를 입력해주세요')
            else:
                prompt = generate_food(
                    country = country,
                    city = city
                )
                response = request_chat_completion(prompt)
                print_streaming_response(response)

# =========================================================================================================
def translator(city):
    url = f"https://dic.daum.net/search.do?q={city}dic=eng"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'html.parser')
    city = soup.select_one('.cleanword_type .sub_txt').get_text(strip=True)
    return city

def hotel_crawling(city,sort,adult,child):
    city = translator(city)

    if sort == '인기순':
        sortField = 'popularityKR'
        sortDirection = 'descending'
    elif sort == '평점 높은순':
        sortField = 'consumerRating'
        sortDirection = 'descending'
    elif sort == '성급 낮은순':
        sortField = 'rating'
        sortDirection = 'ascending'
    elif sort == '성급 높은순':
        sortField = 'rating'
        sortDirection = 'descending'
    elif sort == '가격 낮은순':
        sortField = 'minRate'
        sortDirection = 'ascending'
    elif sort == '가격 높은순':
        sortField = 'minRate'
        sortDirection = 'descending'
    children = []
    if child > 0:
        for i in range(child):
            children.append(12)
    
    url = "https://hotel-api.naver.com/graphql"
    payload = f"{{\"query\":\"query hotelSearchByPlaceFileName($placeFileName: String!, $checkIn: String, $checkOut: String, $adultCnt: Int, $childAges: [Int], $pageSize: Int, $pageIndex: Int, $sortField: String, $sortDirection: String, $starRatings: [Int], $minPrice: Float, $maxPrice: Float, $propertyTypes: [Int], $features: [Int], $guestRatings: [Int], $chains: [Int], $includeTax: Boolean, $impPage: MultiHotelImpPage, $onlyCertStarRating: Boolean) {{\\r\\n  hotelSearchByPlaceFileName(\\r\\n    placeFileName: $placeFileName\\r\\n    checkIn: $checkIn\\r\\n    checkOut: $checkOut\\r\\n    adultCnt: $adultCnt\\r\\n    childAges: $childAges\\r\\n    pageSize: $pageSize\\r\\n    pageIndex: $pageIndex\\r\\n    sortField: $sortField\\r\\n    sortDirection: $sortDirection\\r\\n    starRatings: $starRatings\\r\\n    minPrice: $minPrice\\r\\n    maxPrice: $maxPrice\\r\\n    propertyTypes: $propertyTypes\\r\\n    features: $features\\r\\n    guestRatings: $guestRatings\\r\\n    chains: $chains\\r\\n    includeTax: $includeTax\\r\\n    impPage: $impPage\\r\\n    onlyCertStarRating: $onlyCertStarRating\\r\\n  ) {{\\r\\n    totalCount\\r\\n    hotelSummary {{\\r\\n      propertyTypes {{\\r\\n        hotelCount\\r\\n        name\\r\\n        id\\r\\n      }}\\r\\n      facilities {{\\r\\n        hotelCount\\r\\n        name\\r\\n        id\\r\\n      }}\\r\\n      starRatings {{\\r\\n        value\\r\\n        key\\r\\n      }}\\r\\n      chains {{\\r\\n        hotelCount\\r\\n        name\\r\\n        id\\r\\n      }}\\r\\n      guestRatings {{\\r\\n        value\\r\\n        key\\r\\n      }}\\r\\n      highestTotalRate\\r\\n      lowestTotalRate\\r\\n      totalAvailableResults\\r\\n      totalFilteredResults\\r\\n      postFilterLowestTotalRate\\r\\n    }}\\r\\n    destination {{\\r\\n      placeId\\r\\n      hcPlaceId\\r\\n      placeName\\r\\n      isDomestic\\r\\n      latitude\\r\\n      longitude\\r\\n      placeFileName\\r\\n      placeTypeId\\r\\n      nearByPlaces {{\\r\\n        placeId\\r\\n        hcPlaceId\\r\\n        placeName\\r\\n        isDomestic\\r\\n        latitude\\r\\n        longitude\\r\\n        placeFileName\\r\\n        placeTypeId\\r\\n      }}\\r\\n    }}\\r\\n    hotelList {{\\r\\n      hcHotelId\\r\\n      hotelFileName\\r\\n      hotelName\\r\\n      images\\r\\n      lowestRate\\r\\n      latitude\\r\\n      longitude\\r\\n      guestRating\\r\\n      starRating\\r\\n      address\\r\\n      href\\r\\n      reviewQuotes\\r\\n      isDomestic\\r\\n      rateCount\\r\\n      pkgRateCount\\r\\n      isHotelPKG\\r\\n      country\\r\\n      city\\r\\n      certification {{\\r\\n        starRatingType\\r\\n        starRatingDate\\r\\n      }}\\r\\n      taAwards {{\\r\\n        type\\r\\n        year\\r\\n      }}\\r\\n      hcReviewSummary {{\\r\\n        short\\r\\n        long\\r\\n      }}\\r\\n      topRates {{\\r\\n        hcHotelId\\r\\n        providerHotelId\\r\\n        otaCode\\r\\n        roomName\\r\\n        availableRoomCnt\\r\\n        bookUri\\r\\n        bookUriWithPromotion\\r\\n        npayType\\r\\n        isPayLater\\r\\n        isFreeCancel\\r\\n        isSecretDeal\\r\\n        inclusions\\r\\n        totalRate\\r\\n        gradeDiscount {{\\r\\n          grade\\r\\n          discountRate\\r\\n          originalPrice\\r\\n        }}\\r\\n        roomCategories\\r\\n        isTravelClub\\r\\n        travelClubSavingRate\\r\\n        isPromotion\\r\\n        promotionTotalRate\\r\\n        promotionBenefitRate\\r\\n        promotionBenefitType\\r\\n        promotionBenefitValue\\r\\n        ttpTotalGradeRates {{\\r\\n          grade\\r\\n          landingUri\\r\\n          originalRate\\r\\n          salePercent\\r\\n          saleRate\\r\\n          npaySalePercent\\r\\n          npaySaleRate\\r\\n          hasCoupon\\r\\n          couponRate\\r\\n        }}\\r\\n        ttpGradeRate {{\\r\\n          grade\\r\\n          landingUri\\r\\n          originalRate\\r\\n          salePercent\\r\\n          saleRate\\r\\n          npaySalePercent\\r\\n          npaySaleRate\\r\\n          hasCoupon\\r\\n          couponRate\\r\\n        }}\\r\\n        isKrCoupon\\r\\n        krCouponeRate\\r\\n        gradeDiscount {{\\r\\n          grade\\r\\n          discountRate\\r\\n          originalPrice\\r\\n        }}\\r\\n      }}\\r\\n      pkgRates {{\\r\\n        hcHotelId\\r\\n        providerHotelId\\r\\n        otaCode\\r\\n        roomName\\r\\n        npayType\\r\\n        availableRoomCnt\\r\\n        bookUri\\r\\n        isPayLater\\r\\n        isFreeCancel\\r\\n        inclusions\\r\\n        totalRate\\r\\n        isPromotion\\r\\n        promotionTotalRate\\r\\n        promotionBenefitRate\\r\\n        isTravelClub\\r\\n        travelClubSavingRate\\r\\n      }}\\r\\n    }}\\r\\n  }}\\r\\n}}\\r\\n\",\"variables\":{{\"placeFileName\":\"place:{city}\",\"pageIndex\":0,\"sortField\":\"{sortField}\",\"sortDirection\":\"{sortDirection}\",\"includeTax\":false,\"adultCnt\":{adult},\"childAges\":{children},\"onlyCertStarRating\":false}}}}"
    headers = {
  'authority': 'hotel-api.naver.com',
  'accept': '*/*',
  'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
  'content-type': 'application/json',
  'cookie': 'NNB=UQHVKDO77HUWG; ASID=1b2312aa000001864a186357000052ae; NV_WETR_LAST_ACCESS_RGN_M="MDk2MjAxMDI="; NV_WETR_LOCATION_RGN_M="MDk2MjAxMDI="; _ga=GA1.2.552912219.1697967249; _ga_8P4PY65YZ2=GS1.1.1697967248.1.1.1697967256.52.0.0; _ga_GN4BHVX9DS=GS1.1.1697967251.1.0.1697967256.55.0.0; NID_AUT=cGFL03+g6zgh+rapfq+YCDtI41xqDccCv6Z+9F07IzE/RjX1ZpOYg7xkcNLB7jQx; NID_JKL=91CnsIG7E2fXdppoO1YN1Mw2+ijM+AnL2ISDsxGux08=; nx_ssl=2; NID_SES=AAABsjnxWKFVq5pRUokeEKDGV0h6lFNRqwXvDAFASrDo4QJeT+olwaHW14rqgJHg8xk5VH0pAnNYab+u4cKDZZwZGa19CBY/8dMynKVelSMVlXBQC3jP3B1Mp8In2a4EJYJLvKoUfWmdjePteuyzIBE82CSHmL6dMcYdLHd5uX0ZctPBBL4Y43rF4GJOhM2WEOScimutd3aiYzInBXWkppDSFlkRGE4OjKtl7wVlZ6exSn4SlS5gnRAgq6Lp9IZoxa7jJZ59DcfhHS8kM4uvh2kg9uEaaZwd95LDxBQAQ7IUZj4dSmtWtcp0ZlDxd5R3/eCoOjIjwdazfdJKEdw7gU2DuAXnchfyGfwLRDWSx2IyuNo6ULS5hwvpaVqHU3+MackWXNFrWywt7kyVl2v8KOAhMMwxGEq0Rtid+V8YiZ7GhHIJVPgSEs+Y/oG9pWQAwyT2KqVqMbtNjznD7T5MR92Jm9P277ynOc8OnPfigrhOvs91cAqhqc+Iq7RkWwZOkad+gS1lfvqT/6ff7UaeCNeCVloasnL/3ujTxM+hSxki4ivdWEoTS/gytjcuWnlrzAQyDnSTB7Wki5j48PL/cHfEa7o=; page_uid=iiW8MwqVN8CssAxGLlRssssstUV-436556; NID_SES=AAABtKJh8+pi2eQKNmhgebBIiBAaMqFC0g53wWlGo3BM1hMdGIBFB628Oyon9bywWcRor69WbJyoLNinWL25pC+65M2oZi8y3JZNJgo4jQw2+BFzz/UQQiZZW+LpLWdBLZWGouJ/ZfD3bEEzIqnt4wv4cA7LWoON2d+CXQu7+hozTHOetNzsEsNfJaAfqX0Vr3PhOwiIhf26EPOLkN3SoMDqN+Xx0HO+VXgTEkOs2c52w5nUAPaelkZKHOTuKkzocH2SSIiutrbHsVhicEWIzQrhGPButV6rWOlEYa4aXBNLDUsto3AAuUCSe2BCXtF2nPnK+ABnl/3f2aIpMvCjhmMc9AfYGXh6QayY8Q2qJVZTVcfHhPTPFqjr4wHGboxmcsSU98NOW3QMcfpebVKu9dBbpNljRuOqkJid9btKqA3c4ZKSFEivN6TPAr/Amt7WFOGKXiNGDhfY97F35BGbl5zPs9sbjuTN2/lnaZ6CsHCXVp6s+SMylCMTYE2cR0X1mWZ00CWy5FtvDu61FuwKR3HXuanQYG55P5IgGoO/EIibAvuwijxyQjevIh+NT80XOnb5zW6SaXFpfBxeSK8nTUOdu2Q=',
  'origin': 'https://hotels.naver.com',
  'referer': 'https://hotels.naver.com/list?placeFileName=place%3ALondon&adultCnt=2&includeTax=false&sortField=popularityKR&sortDirection=descending',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
    for hotel in data["data"]["hotelSearchByPlaceFileName"]["hotelList"][:5]:
        hotel_name = hotel["hotelName"]
        review_quotes = hotel["reviewQuotes"]
        rating = hotel['guestRating']
        
        try:
            hotel_images = hotel['images'][0]
            response_image = requests.get(hotel_images)
            image = Image.open(BytesIO(response_image.content))
            resized_image = image.resize((330, 200))
        except (KeyError, IndexError):
            resized_image = None
            
        # response_image = requests.get(hotel_images)
        # image = Image.open(BytesIO(response_image.content))
        # resized_image = image.resize((330,200))
    
        cols = st.columns(2)
        with cols[0]:
            if resized_image:
                st.image([resized_image], width=330)
            else:
                st.write("이미지 없음")
    
        with cols[1]:
            st.write('호텔명 : ', hotel_name)
            st.write('평점 : ', rating)
            if review_quotes:
                for i, feature in enumerate(review_quotes, 1):
                    st.write(f'{i}: "{feature}"')
            else:
                st.write('특징 : 없음')


sorted = ['인기순','평점 높은순','성급 높은순','가격 낮은순','가격 높은순']

with tab_hotel:
    with st.form('form4'):
        st.text('아래의 정보를 입력하세요')
        col1,col2 = st.columns(2)
        with col1:
            country = st.text_input(
                '국가 (필수)'
            )
        with col2:
            city = st.text_input(
                '도시 (필수)'
            )
        col1,col2,col3 = st.columns(3)
        with col1:
            adult = st.number_input(
                '성인',
                min_value = 1,
                max_value = 10,
                step = 1,
                value = 1
            )
        with col2:
            child = st.number_input(
                '아동',
                min_value = 0,
                max_value = 10,
                step = 1,
                value = 0
            )
        with col3:
            sort = st.selectbox(
                '정렬',
                sorted
            )
        submit = st.form_submit_button('제출')
        st.write('제출 후 잠시만 기다려주세요!')
        if submit:
            if not country:
                st.error('국가를 입력해주세요')
            elif not city:
                st.error('도시를 입력해주세요')
            else:
                country = country
                city = city
                adult = adult
                child = child
                sort = sort
                hotel_crawling(city,sort,adult,child)
