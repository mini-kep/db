# TODO: need tests for 'api/desc' post, get, delete methods using `requests` lib and base url for web endpoint 


#GET api/desc?head=GDP&lang=ru   

#Returns:
#   {'head':'GDP', 'ru':'Цена нефти Brent'}  on head
#   All descriptions (head and unit) without parameter

#GET api/desc?unit=rog&lang=en

#Returns:
#    {unit:'rog', en:'rate of growth to previous period'}
#    All descriptions (head and unit) without parameter

#POST api/desc

#Payload:
#[dict(head='BRENT', ru='Цена нефти Brent', en='Brent oil price')
#dict(head='GDP', ru='Валовый внутренний продукт', en='Gross domestic product')
#dict(unit='rog', ru='темп роста к пред. периоду', en='rate of growth to previous period')
#dict(unit='yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')]

#DELETE api/desc?unit=rog   
#DELETE api/desc?head=BRENT
