import falcon
from duan_web import duanWeb
from duan_wechat import duanWechat

app = falcon.API()
duanWeb = duanWeb()
duanWechat = duanWechat()

app.add_route('/web/', duanWeb)
app.add_route('/wechat/', duanWechat)
