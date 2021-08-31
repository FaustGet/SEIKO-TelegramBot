import xml.etree.ElementTree as xml
from dictionary import language

def getSphereCylinder(S:str,C:str):
    if float(C) < 0:
        S = float(S) + float(C)
        C = float(C) * -1
        if float(S) > 0:
            NewSphere =f"+{str(S).replace('.',',')}"
        else:
            NewSphere = str(S).replace('.', ',')
        if float(C) > 0:
            NewCylinder = f"+{str(C).replace('.', ',')}"
        else:
            NewCylinder = str(C).replace('.', ',')
    else:
        NewCylinder = str(C).replace('.', ',')
        NewSphere = str(S).replace('.', ',')
    if len(NewSphere) == 4:
        NewSphere += "0"
    if len(NewCylinder) == 4:
        NewCylinder += "0"
    return NewSphere,NewCylinder

def get_Nomenclature(lens:str,list_keyb:dict,iter = 0):
    try:
        Model = lens
        lens = list_keyb[lens].split(" ")
        list_nomenclature = []
        root_node = xml.parse('Stock.xml').getroot()
        for tag in root_node.findall("Nomenclature"):

            if Model.startswith(tag.attrib['Model']) and tag.attrib['Sphere'] == lens[0] and\
                    tag.attrib['Cylinder'] == lens[1]:

                list_nomenclature.append({
                        "name":f'{Model}',
                        "Code":tag.attrib['Code'],
                        "Model":tag.attrib['Model'],
                        "Amount":tag.attrib['Amount']
                        })
        if len(lens) == 4:
            for tag in root_node.findall("Nomenclature"):
                if Model.startswith(tag.attrib['Model']) and\
                        tag.attrib['Sphere'] == lens[2] and tag.attrib['Cylinder'] == lens[3]:
                    list_nomenclature.append({
                        "name": f'{Model}',
                        "Code": tag.attrib['Code'],
                        "Model": tag.attrib['Model'],
                        "Amount": tag.attrib['Amount']
                    })

        return list_nomenclature
    except:
        if iter<3:
            return get_Nomenclature(Model,list_keyb,iter+1)
        else:
            return []


def ParseXml(S,C,keybrd,lang = "ru",iter=0):
    try:
        print(lang)
        root_node = xml.parse('Stock.xml').getroot()
        list_lens = []
        list_keyb = {}
        find = 0
        for tag in root_node.findall("Nomenclature"):
            if (tag.attrib['Sphere'] == S) and (tag.attrib['Cylinder'] == C):
                if int(tag.attrib['Amount']) > 0:
                    list_lens.append(f"*{tag.attrib['Model']}*\n {language[lang]['Количество линз']}: {tag.attrib['Amount']}")
                    list_keyb.update({tag.attrib['Model']:f'{S} {C}'})
                    keybrd.row(f"{tag.attrib['Model']}" )
                    find = 1
        list_lens.sort()
        return list_lens,find,keybrd,list_keyb
    except:
        if iter<3:
            return ParseXml(S,C,keybrd,lang,iter+1)
        else:
            return [], -1





def ParseCS(S:str,C:str,keybrd,lang = "ru"):
    NewSphere,NewCylinder = getSphereCylinder(S,C)
    print(lang)
    return ParseXml(NewSphere,NewCylinder,keybrd,lang)

def add_new_order(order:dict):
    try:
        filename = "Orders.xml"
        root_node = xml.parse(filename)
        root = xml.Element("Table")
        for tag in root_node.findall("order"):
            root.append(tag)

        appt = xml.Element("order")
        root.append(appt)
        appt.attrib['user'] = order['user']
        appt.attrib['code_user'] = order['code_partner']
        appt.attrib['date'] = order['date']

        items = xml.SubElement(appt, "items")
        for post in order['order']:
            item = xml.SubElement(items, "item")
            item.attrib['name'] = post['name']
            item.attrib['Code'] = post['Code']
            item.attrib['amount'] = str(post['amount'])
        tree = xml.ElementTree(root)
        tree.write(filename)


    except:
        filename = "Orders.xml"
        root = xml.Element("Table")
        appt = xml.Element("order")
        root.append(appt)
        appt.attrib['user'] = order['user']
        appt.attrib['code_user']=order['code_partner']
        appt.attrib['date'] = order['date']

        items = xml.SubElement(appt,"items")
        for post in order['order']:
            item = xml.SubElement(items,"item")
            item.attrib['name'] = post['name']
            item.attrib['Code'] = post['Code']
            item.attrib['amount'] = str(post['amount'])

        tree = xml.ElementTree(root)
        tree.write(filename)
    return





def ParseDoubleXml(S1,C1,S2,C2,keybrd,iter=0,lang = "ru"):
    try:
        root_node = xml.parse('Stock.xml').getroot()
        list_lens1 = {}
        list_lens2 = {}
        list_lens = []
        list_keyb = {}
        find = 0
        for tag in root_node.findall("Nomenclature"):
            if (tag.attrib['Sphere'] == S1) and (tag.attrib['Cylinder'] == C1):
                if int(tag.attrib['Amount']) > 0:
                    list_lens1[tag.attrib['Model']] = tag.attrib['Amount']
            if (tag.attrib['Sphere'] == S2) and (tag.attrib['Cylinder'] == C2):
                if int(tag.attrib['Amount']) > 0:
                    list_lens2[tag.attrib['Model']] = tag.attrib['Amount']
        for post in list_lens1:
            if post in list_lens2:

                if int(list_lens1[post]) > int(list_lens2[post]):
                    list_lens.append(f'*{post}*\n {language[lang]["Количетсво пар"]}: {list_lens2[post]}')
                else:
                    list_lens.append(f'*{post}*\n {language[lang]["Количетсво пар"]}: {list_lens1[post]}')
                find = 1
                list_keyb.update({post:f'{S1} {C1} {S2} {C2}'})
                keybrd.row(f'{post}')
        list_lens.sort()
        return list_lens, find, keybrd,list_keyb
    except:
        if iter<3:
            return ParseDoubleXml(S1,C1,S2,C2,keybrd,iter+1,lang)
        else:
            return [], -1

def ParseDoubleCS(S1:str,C1:str,S2:str,C2:str,keybrd,lang = "ru"):
    NewSphere1, NewCylinder1 = getSphereCylinder(S1, C1)
    NewSphere2, NewCylinder2 = getSphereCylinder(S2, C2)
    return ParseDoubleXml(NewSphere1, NewCylinder1,NewSphere2, NewCylinder2,keybrd,lang)

