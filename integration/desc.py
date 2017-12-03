# TODO: need tests for 'api/desc' post, get, delete methods using `requests` lib and base url for web endpoint 


#GET api/desc?abbr=GDP   

#Returns:
#   {'abbr':'GDP', 'ru':'Цена нефти Brent', 'en':'Brent oil price'}

#GET api/desc?abbr=rog

#Returns:
#    {unit:'rog', en:'rate of growth to previous period', ru='темп роста к пред. периоду'}


#POST api/desc

#Payload:
#[dict(abbr='BRENT', ru='Цена нефти Brent', en='Brent oil price')
#dict(abbr='GDP', ru='Валовый внутренний продукт', en='Gross domestic product')
#dict(abbr='rog', ru='темп роста к пред. периоду', en='rate of growth to previous period')
#dict(abbr='yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')]

#DELETE api/desc?abbr=rog   
#DELETE api/desc?abbr=BRENT
