import json
import jsonpath
from pprint import pprint



# %% RGB格式颜色转换为16进制颜色格式

def rgb2hex(color):
    r = color[0]
    g = color[1]
    b = color[2]
    """将 RGB 颜色转换为十六进制颜色"""
    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
    return hex_color

# %%  磅转像素 DPI 96

def pt2px(value):
    dpi = 96
    px = dpi/72*value
    return px

# %% 判断类别 提取颜色 十六进制 这里我对面填充的类别进行重写
# type:类型
# color：颜色
# opacity：透明度

def judgPolygon(style):
    type = style['type']
    if type == 'CIMSolidFill':
        type='fill_color'
        color = rgb2hex(style['color']['values'])
        opacity = style['color']['values'][3]
    elif type == 'CIMCharacterMarker':
        type='fill_img'
        color = rgb2hex(style['symbol']['symbolLayers'][0]['color']['values'])
        opacity = style['symbol']['symbolLayers'][0]['color']['values'][3]
    elif type == 'CIMHatchFill':
        type='fill_line'
        color = rgb2hex(style['lineSymbol']['symbolLayers'][0]['color']['values'])
        opacity = style['lineSymbol']['symbolLayers'][0]['color']['values'][3]
    elif type == 'CIMSolidStroke':
        type='border_line'
        color = rgb2hex(style['color']['values'])
        opacity = style['color']['values'][3]
    return type,color,opacity
    
# %% 判断是否为使用ttf文件 提取ttf文件名称 文件编号 大小
# fontFamily：文件名称
# chartindex：文件编号
# size:大小

def ttf_img(style):
    if 'fontFamilyName' in style:
        fontFamily = style['fontFamilyName']
        chartindex = hex(style['characterIndex'])
        size = style['size']
        stepX = style['markerPlacement']['stepX']
        stepY = style['markerPlacement']['stepY']
    else:
        fontFamily = None
        chartindex = None
        size = None
        stepX =None
        stepY =None
    return fontFamily,chartindex,size,stepX,stepY
    

# %%  轮廓线 属性

def stroke_line(style):
    type = style['type']
    if type == 'CIMSolidStroke':
        width = style['width']
        linejoin = style['joinStyle']
        linecap = style['capStyle']
    else:
        width = None
        linejoin = None
        linecap = None
    return width,linejoin,linecap

# %%  面填充--线的属性
 
def pology_line(style):
    type = style['type']
    if type == 'CIMHatchFill':
        width = style['lineSymbol']['symbolLayers'][0]['width']
        rotation = style['rotation']
        separation = style['separation']
    else:
        width = None
        rotation = None
        separation = None
    return width,rotation,separation



# %%  一些基础模板
tag_root_mod = '' +\
    '<?xml version="1.0" encoding="UTF-8"?>' +\
    '<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1.0" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" xmlns:se="http://www.opengis.net/se" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">' +\
        '<NamedLayer>' +\
            '<se:Name>%s</se:Name>' +\
            '<UserStyle>' +\
                '<se:Name>%s</se:Name>' +\
                '<se:FeatureTypeStyle>' +\
                '%s' +\
                '</se:FeatureTypeStyle>' +\
            '</UserStyle>' +\
        '</NamedLayer>' +\
    '</StyledLayerDescriptor>'


rule_mod = '' +\
    '<se:Rule>' +\
        '<se:Name>%s</se:Name>' +\
        '<se:Description>' +\
            '<se:Title>%s</se:Title>' +\
        '</se:Description>' +\
        '%s' +\
    '</se:Rule>'

filt_mod = '' +\
    '<ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">' +\
        '<ogc:PropertyIsEqualTo>' +\
            '<ogc:PropertyName>%s</ogc:PropertyName>' +\
            '<ogc:Literal>%s</ogc:Literal>' +\
        '</ogc:PropertyIsEqualTo>' +\
    '</ogc:Filter>'



# %%  borderline 模板
# def borderline_mode(value):
#     if value[0] == 'border_line':
#         BorderLine = '' +\
#             '<se:LineSymbolizer>' +\
#             '<se:Stroke>' +\
#               '<se:SvgParameter name="stroke">%s</se:SvgParameter>' % value[1] +\
#               '<se:SvgParameter name="stroke-width">%s</se:SvgParameter>' % value[11] +\
#               '<se:SvgParameter name="stroke-linejoin">%s</se:SvgParameter>' % value[12] +\
#               '<se:SvgParameter name="stroke-linecap">%s</se:SvgParameter>' % value[13] +\
#             '</se:Stroke>' +\
#             '</se:LineSymbolizer>' 
#     return BorderLine

# %% 面填充 模板

def polygonSymbol_mode(value):
    if value[0] == 'fill_color':
        PolygonSymbol = '' +\
            '<se:PolygonSymbolizer>' +\
                '<se:Fill>' +\
                    '<se:SvgParameter name="fill">%s</se:SvgParameter>' % value[1]      +\
                '</se:Fill>' +\
            '</se:PolygonSymbolizer>'
    elif value[0] == 'fill_img':
        PolygonSymbol = '' +\
            '<se:PolygonSymbolizer>' +\
                '<se:Fill>' +\
                    '<se:GraphicFill>' +\
                        '<se:Graphic>' +\
                            '<se:Mark>' +\
                                '<se:WellKnownName>ttf://%s#%s</se:WellKnownName>' % (value[3],value[4]) +\
                                '<se:Fill>' +\
                                    '<se:SvgParameter name="fill">%s</se:SvgParameter>' % value[1] +\
                                '</se:Fill>' +\
                            '</se:Mark>' +\
                            '<se:Size>%s</se:Size>' % value[5] +\
                        '</se:Graphic>' +\
                    '</se:GraphicFill>' +\
                '</se:Fill>' +\
                '<se:VendorOption name="graphic-margin">%s %s</se:VendorOption>' % (pt2px(value[6]),pt2px(value[6])) +\
            '</se:PolygonSymbolizer>'        
    elif value[0] == 'fill_line':
        PolygonSymbol = '' +\
            '<se:PolygonSymbolizer>' +\
                '<se:Fill>' +\
                    '<se:GraphicFill>' +\
                        '<se:Graphic>' +\
                            '<se:Mark>' +\
                                '<se:WellKnownName>shape://backslash</se:WellKnownName>' +\
                                '<se:Stroke>' +\
                                    '<se:SvgParameter name="stroke">%s</se:SvgParameter>' % value[1] +\
                                    '<se:SvgParameter name="stroke-width">%s</se:SvgParameter>' % value[8] +\
                                '</se:Stroke>' +\
                            '</se:Mark>' +\
                            '<se:Size>%s</se:Size>' % pt2px(value[10]) +\
                            '<se:Rotation>' +\
                                '<ogc:Literal>%s</ogc:Literal>' % (value[9]+45) +\
                            '</se:Rotation>' +\
                        '</se:Graphic>' +\
                    '</se:GraphicFill>' +\
                '</se:Fill>' +\
            '</se:PolygonSymbolizer>' 
    elif value[0] == 'border_line':
        PolygonSymbol = '' +\
            '<se:LineSymbolizer>' +\
            '<se:Stroke>' +\
              '<se:SvgParameter name="stroke">%s</se:SvgParameter>' % value[1] +\
              '<se:SvgParameter name="stroke-width">%s</se:SvgParameter>' % value[11] +\
              '<se:SvgParameter name="stroke-linejoin">%s</se:SvgParameter>' % value[12] +\
              '<se:SvgParameter name="stroke-linecap">%s</se:SvgParameter>' % value[13] +\
            '</se:Stroke>' +\
            '</se:LineSymbolizer>' 
    else:
         PolygonSymbol = None
    return PolygonSymbol




# %% 文件路径与读取

json_text=r'.\source\testPoly.json'
with open(json_text,encoding='utf8') as f:
    content = json.load(f)



# %% 一些全局变量

groups = jsonpath.jsonpath(content, '$..{key_name}'.format(key_name='groups'))[0]

# 字段判断名
prop="".join(groups[0]['heading'])

keys = groups[0]['classes']


# %% 面填充的sld混合

def polygon_mix(styles):
    symbols=[]
    symbols.append(filt_mod % (prop,label))
    for style in styles[::-1]:
        type_value = judgPolygon(style)
        ttf_value = ttf_img(style)
        pology_line_value = pology_line(style)
        stroke_value = stroke_line(style)
        num = type_value+ttf_value+pology_line_value+stroke_value
        symbol_one=polygonSymbol_mode(num)
        symbols.append(symbol_one)
    return symbols

# %% 循环 主路口 获取所需要的值
# num 内包含的顺序分别为：
# 图层类别 颜色 透明度 
# ttf引用名称 ttf图形编号 ttf图形大小 ttf图形X填充（间隔）大小 ttf图形Y填充（间隔）大小
# 图像线填充宽度 图像线填充旋转角度 图像线填充间距 
# 轮廓线宽度 轮廓线样式 轮廓线样式


num_value=[]
groups = []
for key in keys:
    label = ''.join(key['label'])
    field = "".join(key['values'][0]['fieldValues'])
    type_all = key['symbol']['symbol']['type']
    styles = key['symbol']['symbol']['symbolLayers']
    symbols=polygon_mix(styles)
    symbol_all=''.join(symbols)
    rules = rule_mod % (label,label,symbol_all)
    groups.append(rules)

sum=''.join(groups)

tag_root=tag_root_mod % ('testPoly','testPoly',sum)


# %% sld文件创建与输入

sld=open(r'E:\project\lyrx2sld\sld\test.sld','w')

sld.write(tag_root)



