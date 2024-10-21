import os
import yaml

from re import search
from shutil import copy as copyFile
from sys import stdout
from time import time

VERSION = "1.6-SNAPSHOT"


class Color:

    black = '\33[30m'
    red = '\33[31m'
    green = '\33[32m'
    gold = '\33[33m'
    blue = '\33[34m'
    purple = '\33[35m'
    cyan = '\33[36m'
    lightgray = lightgrey = '\33[37m'
    gray = grey = '\33[38m'
    white = reset = '\33[39m'

    bblack = '\33[40m'
    bred = '\33[41m'
    bgreen = '\33[42m'
    bgold = '\33[43m'
    bblue = '\33[44m'
    bpurple = '\33[45m'
    bcyan = '\33[46m'
    blightgray = blightgrey = '\33[47m'
    bgray = bgrey = '\33[48m'
    bwhite = '\33[49m'


def error(string, end='\n'):
    print(f'{Color.red}{string}', end=end)


def loadingPrint(string, newline=False):
    stdout.write('\r' + ' '*100)
    stdout.write('\r' + string)
    if newline:
        stdout.write('\n')
    stdout.flush()


def getYamlContext(file):
    try:
        result = yaml.load(file, Loader=yaml.FullLoader)
        if result is None:
            return {}
        return result
    except FileNotFoundError:
        error(f'File {file} not found.')
        return {}
    except PermissionError:
        error(f'Permission denied: {file}')
        return {}


def checkVersioned(materialType, material):
    global needVersioned
    if materialType in {'VANILLA', 'mc', 'CUSTOM'}:
        if material.upper() in {"GRASS", "SCUTE"}:
            needVersioned = True


def replace_id(d):
    global new
    conditions = []
    z = {key: value for key, value in d.items()}
    for key, value in z.items():
        if isinstance(value, dict):
            replace_id(value)
        elif isinstance(value, str):
            if (
                'id_alias' not in d
                and d.get('material')
                and d.get('material_type', 'mc') == 'mc'
            ):
                material = d.get('material').upper()
                if material == 'GRASS':
                    d['material'] = 'SHORT_GRASS'
                    cond = 'version >= 1.20.3'
                    conditions.append(cond)
                elif material == 'SCUTE':
                    d['material'] = 'TURTLE_SCUTE'
                    cond = 'version >= 1.20.5'
                    conditions.append(cond)

    if conditions != []:
        if 'register' not in new:
            new['register'] = {}
            new['register']['conditions'] = []
        new['register']['conditions'] = conditions


def versionedObjectDump(i=False, o=False):
    global needVersioned, new, key, f1, inputSlots, outputSlots
    if needVersioned:
        new['id_alias'] = key
        replace_id(new)
        filtered_string = ''.join(c for c in key if c.isalpha())
        if filtered_string.islower():
            dump(f1, {'versioned_'+key: new})
        else:
            dump(f1, {'VERSIONED_'+key: new})
        if i:
            f1.write(f"  input: {inputSlots}\n")
        if o:
            f1.write(f"  output: {outputSlots}\n")


def addCommon(number):
    s = str(number)
    k = ""
    c = 1
    for i in s[::-1]:
        k += i
        if c % 3 == 0:
            k += ','
        c += 1
    if c % 3 == 1:
        k = k[:-1]
    return k[::-1]


class CombinedDumper(yaml.Dumper):
    def __init__(self, *args, **kwargs):
        super(CombinedDumper, self).__init__(*args, **kwargs)
        self.sort_keys = lambda x: x

    def ignore_aliases(self, data):
        return True

    def represent_list(self, data):
        return self.represent_sequence('tag:yaml.org,2002:seq', data)

    def represent_mapping(self, tag, mapping, flow_style=None):
        value = []
        node = yaml.MappingNode(tag, value, flow_style=flow_style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        if hasattr(mapping, 'items'):
            mapping = getattr(mapping, 'items')()
        for item_key, item_value in mapping:
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            node_type = yaml.ScalarNode
            if (not (isinstance(node_key, node_type) and not node_key.style) or not (isinstance(node_value, node_type) and not node_value.style)):
                best_style = False
            value.append((node_key, node_value))
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node


CombinedDumper.add_representer(list, CombinedDumper.represent_list)
CombinedDumper.add_representer(dict, CombinedDumper.represent_dict)


def arg_sort(x):
    try:
        return ORDER.index(x[0])
    except ValueError:
        error(f'Unknown key: {x[0]}')
        return len(ORDER)


def dump(file, item):
    yaml.dump(
        item,
        file,
        allow_unicode=True,
        encoding='utf-8',
        Dumper=CombinedDumper,
        sort_keys=arg_sort,
        default_flow_style=False
    )


class config:

    class menus:

        class sections:
            pass

        class machines:
            slots = {}
            inputSlots = []
            outputSlots = []
            progress_slot = 22

        class generators:
            slots = {}
            inputSlots = []
            outputSlots = []
            progress_slot = 22

        class material_generators:
            slots = {}
            outputSlots = []
            progress_slot = 0

    class lores:
        full_copy_slimecustomizer = False

    class additions:

        class categories:
            all = []
            mapping = {}

        class mob_drops:
            all = []
            mapping = {}

        class geo_resources:
            all = []
            mapping = {}

        class items:
            all = []
            mapping = {}

        class capacitors:
            all = []
            mapping = {}

        class machines:
            all = []
            mapping = {}

        class generators:
            all = []
            mapping = {}

        class solar_generators:
            all = []
            mapping = {}

        class material_generators:
            all = []
            mapping = {}

        class researches:
            all = []
            mapping = {}

    class info:
        ...


def encode(item):
    slot = getattr(config.menus.sections, item)
    if item == 'P':
        return {
            'material': 'black_stained_glass_pane',
            'name': '&a',
            'progressbar': True
        }
    if isinstance(slot, str):
        return {
            'material': slot,
            'name': '&a'
        }
    return slot


def readSlots(slots, dt, reader):
    current_slot = 0
    current_item = slots[0][0]
    clazz = getattr(config.menus, dt)
    length = len(slots)
    if reader == BACKGROUND_READER:
        for line in range(length):
            for pos in range(9):
                apos = line*9+pos
                item = slots[line][pos]
                if item == 'P':
                    clazz.progress_slot = apos
                if item != current_item:
                    if apos-1 == current_slot:
                        p = current_slot
                    else:
                        p = f'{current_slot}-{apos-1}'
                    if current_item not in 'ioN':
                        if (dt != 'material_generators' or (dt == 'material_generators' and current_item != 'P')):
                            clazz.slots[p] = encode(current_item)
                    current_slot = apos
                    current_item = item
        if apos == current_slot:
            p = current_slot
        else:
            p = f'{current_slot}-{apos}'
        if current_item not in 'ioN':
            clazz.slots[p] = encode(current_item)
    elif reader == INPUT_READER:
        for line in range(length):
            for pos in range(9):
                apos = line*9+pos
                item = slots[line][pos]
                if item == 'i':
                    clazz.inputSlots.append(apos)
    elif reader == OUTPUT_READER:
        for line in range(length):
            for pos in range(9):
                apos = line*9+pos
                item = slots[line][pos]
                if item == 'o':
                    clazz.outputSlots.append(apos)


def copyTo(new_string, old_string, translate={}):
    global new, data
    new_split1 = new_string.split('.')
    old_split1 = old_string.split('.')

    new_split = []
    for a in new_split1:
        try:
            if a[0] == a[-1] and a[0] in {'\'', '\"'}:
                new_split.append(a[1:-1])
            else:
                new_split.append(int(a))
        except ValueError:
            new_split.append(a)
    old_split = []
    for a in old_split1:
        try:
            old_split.append(int(a))
        except ValueError:
            old_split.append(a)

    ndat = new
    odat = data
    for dddkey in old_split:
        try:
            odat = odat[dddkey]
        except KeyError:
            try:
                odat = odat[str(dddkey)]
            except KeyError:
                odat = NULL
    for dddkey in new_split:
        if dddkey == new_split[-1]:
            ndat[dddkey] = odat
            break
        if dddkey not in ndat:
            ndat[dddkey] = {}
        ndat = ndat[dddkey]
    if translate != {}:
        ndat[dddkey] = translate.get(odat, odat)


def replaceColor(item):
    while True:
        match1 = search(r'(&|§)x((&|§)[0-9A-Fa-f]){6}', item)

        if match1 is None:
            break

        code = match1.group()
        temp = hexColorForm.format(
            code[3], code[5], code[7], code[9], code[11], code[13]
            )
        if config.colorMode == 'cmi':
            temp = '{' + temp + '}'
        item = item.replace(code, temp)

    for char in 'lmnok':
        while True:
            match1 = search(
                f'(&|§){char}((?!(&|§)).)*((&|§)(\d|[A-Fa-f]|#))?', item)
            if match1 is None:
                break
            match2 = match1.group()
            replace_char = None
            if match2[-1] in '0123456789abcdefABCDEF#':
                match2 = match2[:-1]
            if config.colorMode == 'minedown':
                charv = CHARS[char]
                replace_char = match2.replace(f'&{char}', f'{charv}')
                if match2[-1] == '&':
                    replace_char = replace_char.replace('&', f'{charv}&')
                elif match2[-1] == '§':
                    replace_char = replace_char.replace('§', f'{charv}§')
                else:
                    replace_char += charv
                item = item.replace(match2, replace_char)
                item = item.replace(charv*2, charv)
            elif config.colorMode == 'minimessage':
                charv = CHARS2[char]
                replace_char = match2.replace(f'&{char}', f'{charv}')
                item = item.replace(match2, replace_char)
            if replace_char is None:
                break
    return item


def copyName(key='item-name'):
    global new, data
    name = data[key]

    if name == "":
        return

    name = replaceColor(name)
    if 'item' not in new:
        new['item'] = {}
    new['item']['name'] = name


def copyLore(key='item-lore'):
    global new, data
    lores = data.get(key, [])

    if lores == []:
        if config.lores.full_copy_slimecustomizer:
            new['item']['lore'] = []
        return

    new_lores = []
    if isinstance(lores, list):
        for lore in lores:
            new_lores.append(replaceColor(lore))
    if 'item' not in new:
        new['item'] = {}
    new['item']['lore'] = new_lores


def copyRecipe():
    global new, data
    for dkey in data['crafting-recipe']:
        ct = data['crafting-recipe'][dkey]['type']
        if ct == 'VANILLA' and data['crafting-recipe'][dkey]['id'] != 'AIR':
            copyTo(
                f'recipe.{dkey}.material_type',
                f'crafting-recipe.{dkey}.type'
            )
            new['recipe'][int(dkey)]['material_type'] = 'none'
        if ct != "NONE":
            copyTo(
                f'recipe.{dkey}.material_type',
                f'crafting-recipe.{dkey}.type', itemType
            )
            copyTo(f'recipe.{dkey}.material', f'crafting-recipe.{dkey}.id')
            copyTo(f'recipe.{dkey}.amount', f'crafting-recipe.{dkey}.amount')
            checkVersioned(ct, data['crafting-recipe'][dkey]['id'])


def copyRecipes():
    global new, data
    for dkey in data['recipes']:
        recipe = data['recipes'][dkey]
        copyTo(
            f'recipes.\"{dkey}\".seconds',
            f'recipes.{dkey}.speed-in-seconds'
        )
        for opera in {'input', 'output'}:
            for iterNum in {1, 2}:
                try:
                    if str(iterNum) in recipe[opera]:
                        cfg = recipe[opera][str(iterNum)]
                    else:
                        cfg = recipe[opera][iterNum]
                except KeyError:
                    continue
                mt = cfg['type']
                checkVersioned(mt, cfg['id'])
                if mt == 'VANILLA' and cfg['id'].upper() == 'AIR':
                    nr = new['recipes'][f"{dkey}"]
                    if opera not in nr:
                        nr[opera] = {}
                    if iterNum not in nr[opera]:
                        nr[opera][iterNum] = {}
                    nr[opera][iterNum]['material_type'] = 'none'
                elif mt != 'NONE':
                    oldPrefix = f"recipes.{dkey}.{opera}.{iterNum}"
                    newPrefix = f"recipes.\"{dkey}\".{opera}.{iterNum}"
                    copyTo(
                        f'{newPrefix}.material_type',
                        f'{oldPrefix}.type',
                        itemType
                    )
                    copyTo(f'{newPrefix}.material', f'{oldPrefix}.id')
                    copyTo(f'{newPrefix}.amount', f'{oldPrefix}.amount')


def copyRecipesGenerator():
    global new, data
    for dkey in data['recipes']:
        copyTo(
            f'fuels.\"{dkey}\".seconds',
            f'recipes.{dkey}.time-in-seconds',
        )
        recipe = data['recipes'][dkey]
        mt = recipe['input']['type']
        if mt != 'NONE' or (
            mt == 'VANILLA'
            and recipe['input']['id'].upper() != 'AIR'
        ):
            oldPrefix = f"recipes.{dkey}.input"
            newPrefix = f"fuels.\"{dkey}\".item"
            copyTo(f'{newPrefix}.material_type', f'{oldPrefix}.type', itemType)
            copyTo(f'{newPrefix}.material', f'{oldPrefix}.id')
            copyTo(f'{newPrefix}.amount', f'{oldPrefix}.amount')
            item = new['fuels'][dkey]['item']
            checkVersioned(mt, item['material'])
        mt = data['recipes'][dkey]['output']['type']
        if mt != 'NONE' or (
            mt == 'VANILLA'
            and recipe['output']['id'].upper() != 'AIR'
        ):
            newPrefix = f"fuels.\"{dkey}\".output"
            oldPrefix = f"recipes.{dkey}.output"
            copyTo(f'{newPrefix}.material_type', f'{oldPrefix}.type', itemType)
            copyTo(f'{newPrefix}.material', f'{oldPrefix}.id')
            copyTo(f'{newPrefix}.amount', f'{oldPrefix}.amount')
            item = new['fuels'][dkey]['output']
            checkVersioned(mt, item['material'])


def copyGroup():
    global new, data
    group = data['category']
    if "existing:" in group:
        split = group.split(':')
        new['item_group'] = f'{split[1]}:{split[2]}'
    else:
        if config.groupMode == 'prefix':
            new['item_group'] = 'rsc_'+group
        elif config.groupMode == 'namespace':
            new['item_group'] = 'rykenslimecustomizer:'+group
        else:
            new['item_group'] = group


def readConfig():
    global hexColorForm
    with open('translate_config.yml', 'r', encoding='utf-8') as f:
        cfg = getYamlContext(f)
        config.outputFolder = cfg.get('outputFolder', "translated")
        config.colorMode = cfg.get('colorMode', "cmi")
        config.groupMode = cfg.get('groupMode', "none")
        config.setAllSaveditems_v = cfg.get('setAllSaveditems_v', "none")
        config.enableCreateVersionedObject = cfg.get('enableCreateVersionedObject', False)
        menu = cfg['menus']
        cmenu = config.menus
        for section, value in menu['sections'].items():
            setattr(cmenu.sections, section, value)
        cmenu.machines.title = menu['machines']['title']
        cmenu.generators.title = menu['generators']['title']
        cmenu.material_generators.title = menu['material-generators']['title']
        readSlots(menu['machines']['background-slots'], 'machines', BACKGROUND_READER)
        readSlots(menu['machines']['input-slots'], 'machines', INPUT_READER)
        readSlots(menu['machines']['output-slots'], 'machines', OUTPUT_READER)
        readSlots(menu['generators']['background-slots'], 'generators', BACKGROUND_READER)
        readSlots(menu['generators']['input-slots'], 'generators', INPUT_READER)
        readSlots(menu['generators']['output-slots'], 'generators', OUTPUT_READER)
        readSlots(menu['material-generators']['background-slots'], 'material_generators', BACKGROUND_READER)
        readSlots(menu['material-generators']['output-slots'], 'material_generators', OUTPUT_READER)
        config.lores.full_copy_slimecustomizer = cfg['lores'].get(
            'full-copy-slimecustomizer'
        )
        if config.lores.full_copy_slimecustomizer:
            print(f'''{Color.cyan} You have already enabled full-copy-slimecustomizer.''')
        hexColorForm = {
            "vanilla": "&#{}{}{}{}{}{}",
            "vanilla2": "&x&{}&{}&{}&{}&{}&{}",
            "cmi": "#{}{}{}{}{}{}",
            "minimessage": "<#{}{}{}{}{}{}>",
            "minedown": "&#{}{}{}{}{}{}&"
        }[config.colorMode]

        additions = cfg['additions']
        for key, value in additions.items():
            p = getattr(config.additions, key)
            setattr(p, 'mapping', {})
            setattr(p, 'all', False)
            if value != {}:
                for group_context in value.values():
                    for item in group_context['items']:
                        if item == '__all__':
                            setattr(p, 'all', True)
                        p.mapping[item] = group_context['config']

    if not os.path.isabs(config.outputFolder):
        current_dir = os.getcwd()
        config.outputFolder = os.path.join(current_dir, config.outputFolder)

    os.makedirs(config.outputFolder, exist_ok=True)
    info = cfg['info']
    config.info.enable = info['enable']
    if config.info.enable:
        config.info.id = info['id']
        config.info.name = info['name']
        config.info.depends = info['depends']
        config.info.pluginDepends = info['pluginDepends']
        config.info.scriptListener = info['scriptListener']
        config.info.version = info['version']
        config.info.description = info['description']
        config.info.authors = info['authors']
        config.info.repo = info['repo']


def getPath(file_name):
    return os.path.join(config.outputFolder, file_name)


def loadAdditions(p, items, key):
    if key in p.mapping:
        mapping = p.mapping[key]
    if p.all:
        mapping = p.mapping['__all__']
    else:
        return
    mk = tuple(mapping.keys())[0]
    mv = tuple(mapping.values())[0]
    items[key][mk] = mv


def generateBase():
    folders = (
        f"{config.outputFolder}",
        f"{config.outputFolder}/saveditems",
        f"{config.outputFolder}/scripts"
    )
    for folder in folders:
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass

    for file_name in os.listdir("saveditems"):
        file_path = os.path.join("saveditems", file_name)
        if os.path.isfile(file_path):
            copyFile(file_path, f"{config.outputFolder}/saveditems")
            if config.setAllSaveditems_v != 'none':
                with open(f"{config.outputFolder}/saveditems/{file_name}", 'w', encoding='utf-8') as f1, open(file_path, 'r', encoding='utf-8') as f2:
                    text = f2.readlines()
                    text[2] = f'  v: {config.setAllSaveditems_v}\n'
                    f1.write(''.join(text))

    files = (
        "machines.yml",
        "simple_machines.yml",
        "mb_machines.yml",
        "armors.yml",
        "recipe_types.yml",
        "foods.yml",
        "supers.yml",
        "template_machines.yml"
    )
    for file_name in files:
        with open(getPath(file_name), 'w', encoding='utf-8') as f:
            f.write('\n')


def translateInfo():
    global new, data
    with open(getPath('info.yml'), 'w', encoding='utf-8') as f1:
        with open('sc-addon.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{Color.gold}Translating{Color.green} sc-addon.yml')

            if config.info.enable:
                items = {
                    'id': config.info.id,
                    'name': config.info.name,
                    'depends': config.info.depends,
                    'pluginDepends': config.info.pluginDepends,
                    'scriptListener': config.info.scriptListener,
                    'version': config.info.version,
                    'description': config.info.description,
                    'authors': config.info.authors,
                    'repo': config.info.repo
                }
            else:
                items = {
                    'id': "ChangeMe",
                    'name': "ChangeMe",
                    'depends': [],
                    'pluginDepends': [],
                    'scriptListener': "",
                    'version': "ChangeMe",
                    'description': "ChangeMe",
                    'authors': ["SlimeReloadingProject"],
                    'repo': ""
                }
            data = getYamlContext(f2)
            depend = data.get('depend', [])
            if 'Slimefun' in depend:
                depend.remove('Slimefun')
            items['pluginDepends'] = depend
            dump(f1, items)
    loadingPrint(f'{Color.green}sc-addon.yml √', True)


def translateGroups():
    global new, data, needVersioned, f1, key
    with open(getPath('groups.yml'), 'w', encoding='utf-8') as f1:
        with open('categories.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} categories.yml {Color.gold}{c} / {Color.green}{ld}')
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                if config.groupMode == 'prefix':
                    key = 'rsc_'+key
                new = items[key] = {}
                new['lateInit'] = False
                t = data.get('type', 'normal')

                if 'parent' in data:
                    if data['parent'] == 'this':
                        t = 'nested'
                    else:
                        t = 'sub'
                new['type'] = t
                new['item'] = {}
                dtype = 'mc'
                ditem = data['category-item']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    s = data['category-item'][5:]
                    new['item']['material'] = s
                    if (s.startswith("ey") or s.startswith("ew")):
                        new['item']['material_type'] = dtype = "skull_base64"
                else:
                    copyTo('item.material', 'category-item')
                checkVersioned(dtype, ditem)
                copyName('category-name')
                if t == 'sub':
                    cat = data['parent']
                    if "existing:" in cat:
                        split = cat.split(':')
                        new['parent'] = f'{split[1]}:{split[2]}'
                    else:
                        if config.groupMode == 'prefix':
                            new['parent'] = 'rsc_'+cat
                        elif config.groupMode == 'namespace':
                            new['parent'] = 'rykenslimecustomizer:'+cat
                        else:
                            new['parent'] = cat
                elif t == 'seasonal':
                    copyTo('month', 'month')
                elif t == 'locked':
                    copyTo('parents', 'parents')
                if 'tier' in data:
                    copyTo('tier', 'tier')

                p = config.additions.categories
                loadAdditions(p, items, key)
                dump(f1, items)
                if config.enableCreateVersionedObject:
                    versionedObjectDump()
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} categories.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}categories.yml √', True)


def translateMobDrops():
    global new, data, needVersioned, f1, key
    with open(getPath('mob_drops.yml'), 'w', encoding='utf-8') as f1:
        with open('mob-drops.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} mob-drops.yml {Color.gold}{c} / {Color.green}{ld}')
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName()
                copyLore()
                if (
                    data['item-id'].startswith('SKULL')
                    and data['item-type'] == 'CUSTOM'
                ):
                    new['item']['material_type'] = 'skull_hash'
                    s = data['item-id'][5:]
                    new['item']['material'] = s
                    if (s.startswith("ey") or s.startswith("ew")):
                        new['item']['material_type'] = "skull_base64"
                else:
                    copyTo('item.material_type', 'item-type', defineType)
                    copyTo('item.material', 'item-id')
                copyTo('item.amount', 'item-amount')

                copyTo('entity', 'mob')
                copyTo('chance', 'chance')

                p = config.additions.mob_drops
                loadAdditions(p, items, key)
                dump(f1, items)
                if config.enableCreateVersionedObject:
                    versionedObjectDump()
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} mob-drops.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}mob-drops.yml √', True)


def translateGeoResources():
    global new, data, needVersioned, f1, key
    with open(getPath('geo_resources.yml'), 'w', encoding='utf-8') as f1:
        with open('geo-resources.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} geo-resources.yml {Color.gold}{c} / {Color.green}{ld}')
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName()
                copyLore()
                dtype = data['item-type']
                ditem = data['item-id']
                if ditem.startswith('SKULL') and dtype == 'CUSTOM':
                    new['item']['material_type'] = 'skull_hash'
                    s = data['item-id'][5:]
                    new['item']['material'] = s
                    if (s.startswith("ey") or s.startswith("ew")):
                        new['item']['material_type'] = "skull_base64"
                else:
                    copyTo('item.material_type', 'item-type', defineType)
                    copyTo('item.material', 'item-id')
                checkVersioned(dtype, ditem)
                copyTo('max_deviation', 'max-deviation')
                copyTo('geo_name', 'item-name')
                new['recipe_type'] = 'GEO_MINER'
                new['obtain_from_geo_miner'] = True
                new['supply'] = supply = {}
                supply['normal'] = {}
                supply['nether'] = {}
                supply['the_end'] = {}
                biomes = data.get('biome', NULL)
                if biomes != NULL:
                    biomes = {
                        biomeName.lower(): number
                        for biomeName, number in biomes.items()
                    }
                    supply['normal'] = biomes
                    supply['nether'] = biomes
                    supply['the_end'] = biomes
                envs = data.get('environment', NULL)
                if envs != NULL:
                    if envs.get('NORMAL', 0) != 0:
                        if supply['normal'] == {}:
                            supply['normal'] = envs.get('NORMAL')
                        else:
                            supply['normal']['others'] = envs.get('NORMAL')
                    if envs.get('NETHER', 0) != 0:
                        if supply['nether'] == {}:
                            supply['nether'] = envs.get('NETHER')
                        else:
                            supply['nether']['others'] = envs.get('NETHER')
                    if envs.get('THE_END', 0) != 0:
                        if supply['the_end'] == {}:
                            supply['the_end'] = envs.get('THE_END')
                        else:
                            supply['the_end']['others'] = envs.get('THE_END')
                if supply == {}:
                    del supply, new['supply']
                else:
                    if supply['normal'] == {}:
                        del supply['normal']
                    if supply['nether'] == {}:
                        del supply['nether']
                    if supply['the_end'] == {}:
                        del supply['the_end']

                p = config.additions.geo_resources
                loadAdditions(p, items, key)
                dump(f1, items)
                if config.enableCreateVersionedObject:
                    versionedObjectDump()
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} geo-resources.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}geo-resources.yml √', True)


def translateItems():
    global new, data, needVersioned, f1, key
    with open(getPath('items.yml'), 'w', encoding='utf-8') as f1:
        with open('items.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} items.yml {Color.gold}{c} / {Color.green}{ld}')
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                dt = data['item-type']
                copyGroup()
                if dt == "CUSTOM":
                    name = replaceColor(data['item-name'])
                    if 'item' not in new:
                        new['item'] = {}
                    new['item']['name'] = name
                    lores = data.get('item-lore', [])
                    new_lores = []
                    if isinstance(lores, list):
                        for lore in lores:
                            new_lores.append(replaceColor(lore))
                    if 'item' not in new:
                        new['item'] = {}
                    new['item']['lore'] = new_lores
                ditem = str(data['item-id'])
                if ditem.startswith('SKULL') and dt == 'CUSTOM':
                    new['item']['material_type'] = dt = 'skull_hash'
                    s = data['item-id'][5:]
                    new['item']['material'] = s
                    if (s.startswith("ey") or s.startswith("ew")):
                        new['item']['material_type'] = dt = "skull_base64"
                else:
                    copyTo('item.material_type', 'item-type', defineType)
                    copyTo('item.material', 'item-id')
                checkVersioned(dt, ditem)
                copyTo('item.amount', 'item-amount')
                copyTo('placeable', 'placeable', {NULL: False})
                copyTo('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()

                p = config.additions.items
                loadAdditions(p, items, key)
                dump(f1, items)
                if config.enableCreateVersionedObject:
                    versionedObjectDump()
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} items.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}items.yml √', True)


def translateCapacitors():
    global new, data, needVersioned, f1, key
    with open(getPath('capacitors.yml'), 'w', encoding='utf-8') as f1:
        with open('capacitors.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} capacitors.yml {Color.gold}{c} / {Color.green}{ld}')
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName('capacitor-name')
                copyLore('capacitor-lore')
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] = new['item']['lore']+[
                        "&e电容",
                        f"&8⇨ &e⚡&7 {addCommon(data['capacity'])} J 可存储",
                    ]
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    s = data['block-type'][5:]
                    new['item']['material'] = s
                    if s.startswith("ey") or s.startswith("ew"):
                        new['item']['material_type'] = dtype = "skull_base64"
                elif data['block-type'] in ('DEFAULT', 'default'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    new['item']['material'] = CAPA_SKULL
                else:
                    copyTo('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                copyTo('item.amount', 'item-amount')

                copyTo('capacity', 'capacity')
                copyTo('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()

                p = config.additions.capacitors
                loadAdditions(p, items, key)
                dump(f1, items)
                if config.enableCreateVersionedObject:
                    versionedObjectDump()
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} capacitors.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}capacitors.yml √', True)


def translateMachines():
    global new, data, needVersioned, f1, key, inputSlots, outputSlots
    with open(getPath('recipe_machines.yml'), 'w', encoding='utf-8') as f1:
        inputSlots = config.menus.machines.inputSlots
        outputSlots = config.menus.machines.outputSlots
        with open('machines.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} machines.yml {Color.gold}{c} / {Color.green}{ld}')
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                menus['machines'].append({
                    'iden': key,
                    'name': data['machine-name'],
                    'progressBarItem': data['progress-bar-item']
                })
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName('machine-name')
                copyLore('machine-lore')
                SCMachineLore = [
                    "&b机器",
                    f"&8⇨ &e⚡&7 {addCommon(data['stats']['energy-buffer'])} J 可存储",
                    f"&8⇨ &e⚡&7 {addCommon(data['stats']['energy-consumption']*2)} J/s",
                ]
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] += SCMachineLore
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    s = data['block-type'][5:]
                    new['item']['material'] = s
                    if s.startswith("ey") or s.startswith("ew"):
                        new['item']['material_type'] = dtype = "skull_base64"
                else:
                    copyTo('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                new['speed'] = 1
                copyTo('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                copyTo('capacity', 'stats.energy-buffer')
                copyTo('energyPerCraft', 'stats.energy-consumption')
                copyRecipes()

                p = config.additions.machines
                loadAdditions(p, items, key)
                dump(f1, items)
                f1.write(f'  input: {inputSlots}\n  output: {outputSlots}\n')
                if config.enableCreateVersionedObject:
                    versionedObjectDump(i=True, o=True)
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} machines.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}machines.yml √', True)


def translateGenerators():
    global new, data, needVersioned, f1, key, inputSlots, outputSlots
    with open(getPath('generators.yml'), 'w', encoding='utf-8') as f1:
        inputSlots = config.menus.generators.inputSlots
        outputSlots = config.menus.generators.outputSlots
        with open('generators.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} generators.yml {Color.gold}{c} / {Color.green}{ld}')
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                menus['generators'].append({
                    'iden': key,
                    'name': data['generator-name'],
                    'progressBarItem': data['progress-bar-item']
                })
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName('generator-name')
                copyLore('generator-lore')
                SCGeneratorLore = [
                    "&a发电机",
                    f"&8⇨ &e⚡&7 {addCommon(data['stats']['energy-buffer'])} J 可存储",
                    f"&8⇨ &e⚡&7 {addCommon(data['stats']['energy-production']*2)} J/s",
                ]
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] += SCGeneratorLore
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    s = data['block-type'][5:]
                    new['item']['material'] = s
                    if s.startswith("ey") or s.startswith("ew"):
                        new['item']['material_type'] = dtype = "skull_base64"
                else:
                    copyTo('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                copyTo('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                copyTo('capacity', 'stats.energy-buffer')
                copyTo('production', 'stats.energy-production')
                copyRecipesGenerator()

                p = config.additions.generators
                loadAdditions(p, items, key)
                dump(f1, items)
                f1.write(f"  input: {inputSlots}\n  output: {outputSlots}\n")
                if config.enableCreateVersionedObject:
                    versionedObjectDump(i=True, o=True)
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} generators.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}generators.yml √', True)


def translateSolarGenerators():
    global new, data, needVersioned, f1, key
    with open(getPath('solar_generators.yml'), 'w', encoding='utf-8') as f1:
        with open('solar-generators.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} solar-generators.yml {Color.gold}{c} / {Color.green}{ld}')
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName('generator-name')
                copyLore('generator-lore')
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    s = data['block-type'][5:]
                    new['item']['material'] = s
                    if s.startswith("ey") or s.startswith("ew"):
                        new['item']['material_type'] = dtype = "skull_base64"
                else:
                    copyTo('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                copyTo('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                new['lightLevel'] = 1
                dep = data['stats']['energy-production']
                de = dep['day']
                ne = dep['night']
                SCSolarGeneratorLore = [
                    "&e太阳能发电机",
                    f"&8⇨ &e⚡&7 {addCommon(de*2)} J/s (昼)",
                    f"&8⇨ &e⚡&7 {addCommon(ne*2)} J/s (夜)",
                ]
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] += SCSolarGeneratorLore
                new['dayEnergy'] = de
                new['nightEnergy'] = ne
                new['capacity'] = max(de, ne)

                p = config.additions.solar_generators
                loadAdditions(p, items, key)
                dump(f1, items)
                if config.enableCreateVersionedObject:
                    versionedObjectDump()
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} solar-generators.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}solar-generators.yml √', True)


def translateMaterialGenerators():
    global new, data, needVersioned, f1, key, outputSlots
    with open(getPath('mat_generators.yml'), 'w', encoding='utf-8') as f1:
        with open('material-generators.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} material-generators.yml {Color.gold}{c} / {Color.green}{ld}')
            outputSlots = config.menus.material_generators.outputSlots
            progress_slot = config.menus.material_generators.progress_slot
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                menus['material-generators'].append({
                    'iden': key,
                    'name': data['item-name']
                })
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName()
                copyLore()
                SCMaterialGeneratorLore = [
                    "&e材料生成器",
                    f"&8⇨ &7速度: &b每 {data['output']['tick-rate']} 粘液刻生成一次",
                    f"&8⇨ &e⚡&7 {addCommon(data['stats']['energy-buffer'])} J 可存储",
                    f"&8⇨ &e⚡&7 {addCommon(data['stats']['energy-consumption']*2)} J/s",
                ]
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] += SCMaterialGeneratorLore
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    s = data['block-type'][5:]
                    new['item']['material'] = s
                    if s.startswith("ey") or s.startswith("ew"):
                        new['item']['material_type'] = dtype = "skull_base64"
                else:
                    copyTo('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                copyTo('capacity', 'stats.energy-buffer')
                copyTo('per', 'stats.energy-consumption')
                copyTo('item.amount', 'item-amount')
                copyTo('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                new['status'] = progress_slot
                copyTo('tickRate', 'output.tick-rate')
                if (
                    data['output']['type'] == 'VANILLA'
                    and data['output']['id'].upper() == 'AIR'
                ):
                    new['outputItem'] = {}
                    new['outputItem']['material_type'] = 'none'
                else:
                    copyTo('outputItem.material_type', 'output.type', itemType)
                    copyTo('outputItem.material', 'output.id')
                    copyTo('outputItem.amount', 'output.amount')
                    checkVersioned(
                        new['outputItem']['material_type'],
                        new['outputItem']['material']
                    )

                p = config.additions.material_generators
                loadAdditions(p, items, key)
                dump(f1, items)
                f1.write(f"  output: {outputSlots}\n")
                if config.enableCreateVersionedObject:
                    versionedObjectDump(o=True)
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} material-generators.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}material-generators.yml √', True)


def translateResearches():
    global new, data, needVersioned, f1, key
    with open(getPath('researches.yml'), 'w', encoding='utf-8') as f1:
        with open('researches.yml', 'r', encoding='utf-8') as f2:
            d = getYamlContext(f2)
            c = 0
            ld = len(d)
            loadingPrint(f'{Color.gold}Translating{Color.green} researches.yml {Color.gold}{c} / {Color.green}{ld}')
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                copyTo('id', 'id')
                copyTo('name', 'name')
                copyTo('levelCost', 'cost')
                copyTo('items', 'items')

                p = config.additions.researches
                loadAdditions(p, items, key)
                dump(f1, items)
                if config.enableCreateVersionedObject:
                    versionedObjectDump()
                c += 1
                loadingPrint(f'{Color.gold}Translating{Color.green} researches.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}researches.yml √', True)


def generateMenus():
    global new, data, needVersioned, f1, key
    with open(getPath('menus.yml'), 'w', encoding='utf-8') as f1:
        c = 0
        ld = len(menus['machines']+menus['generators']+menus['material-generators'])
        loadingPrint(f'{Color.gold}Generating{Color.green} meuns.yml {Color.gold}{c} / {Color.green}{ld}')
        cfg = config.menus.machines
        progress_slot = cfg.progress_slot
        for menu in menus['machines']:
            items = {}
            iden = menu['iden']
            name = menu['name']
            progress_item = menu['progressBarItem']
            items[iden] = {
                "title": replaceColor(cfg.title.replace('%name%', name)),
                "slots": cfg.slots
            }
            items[iden]['slots'][progress_slot]['progressBarItem'] = {}
            items[iden]['slots'][progress_slot]['progressBarItem']['material'] = progress_item
            dump(f1, items)
            c += 1
            loadingPrint(f'{Color.gold}Generating{Color.green} meuns.yml {Color.gold}{c} / {Color.green}{ld}')
        cfg = config.menus.generators
        progress_slot = cfg.progress_slot
        for menu in menus['generators']:
            items = {}
            iden = menu['iden']
            name = menu['name']
            progress_item = menu['progressBarItem']
            items[iden] = {
                "title": replaceColor(cfg.title.replace('%name%', name)),
                "slots": cfg.slots
            }
            items[iden]['slots'][progress_slot]['progressBarItem'] = {}
            items[iden]['slots'][progress_slot]['progressBarItem']['material'] = progress_item
            dump(f1, items)
            c += 1
            loadingPrint(f'{Color.gold}Generating{Color.green} meuns.yml {Color.gold}{c} / {Color.green}{ld}')
        cfg = config.menus.material_generators
        for menu in menus['material-generators']:
            items = {}
            iden = menu['iden']
            name = menu['name']
            items[iden] = {
                "title": replaceColor(cfg.title.replace('%name%', name)),
                "slots": cfg.slots
            }
            dump(f1, items)
            c += 1
            loadingPrint(f'{Color.gold}Generating{Color.green} meuns.yml {Color.gold}{c} / {Color.green}{ld}')
    loadingPrint(f'{Color.green}meuns.yml √', True)


def createFile(file_name, text=''):
    if isinstance(file_name, tuple):
        text = file_name[1]
        file_name = file_name[0]
    with open(getPath(file_name), 'w', encoding='utf-8') as f:
        f.write(f'\n{text}')
        loadingPrint(f'{Color.green}{file_name} √', True)


menus = {'machines': [], 'generators': [], 'material-generators': []}
itemType = {
    'VANILLA': 'mc',
    'SLIMEFUN': 'slimefun',
    'NONE': 'none',
    'SAVEDITEM': 'saveditem'
}
defineType = {
    'CUSTOM': 'mc',
    'SAVEDITEM': 'saveditem'
}

needVersioned = False
ORDER = ('id_alias', 'lateinit', 'register', 'totalTicks', 'type', 'tier', 'hidden', 'protection_types', 'fullSet', 'item_group', 'helmet', 'chestplate', 'leggings', 'boots', 'placeable', 'item', 'id', 'material_type', 'material', 'name', 'modelId', 'glow', 'lore', 'amount', 'progressbar', 'progressBarItem', 'script', 'class', 'arg_template', 'args', 'field', 'method', 'recipe_type', 'recipe', 'input', 'output', 'work', 'sound', 'max_deviation', 'obtain_from_geo_miner', 'geo_name', 'entity', 'chance', 'supply', 'world', 'nether', 'the_end', 'energy_capacity', 'radiation', 'rainbow', 'rainbow_materials', 'anti_wither', 'souldbound', 'pinglin_trade_chance', 'vanilla', 'potion_effects', 'energy', 'settings', 'capacity', 'production', 'title', 'slots', 'import', 'fuels', 'item', 'seconds', 'chooseOne', 'dayEnergy', 'nightEnergy', 'lightLevel', 'outputItem', 'tickRate', 'status', 'per', 'energyPerCraft', 'consumption', 'speed', 'recipes', 'levelCost', 'currencyCost', 'items', 'drop_from', 'drop_chance', 'drop_amount')
CAPA_SKULL = '91361e576b493cbfdfae328661cedd1add55fab4e5eb418b92cebf6275f8bb4'
CHARS = {'n': '__', 'm': '~~', 'k': '??', 'l': '**', 'o': '##'}
CHARS2 = {'l': '<l>', 'n': '<u>', 'o': '<i>', 'k': '<obf>', 'm': '<st>'}
NULL = '__SC_TO_RSC_NOT_FOUND_ARGUMENT'
BACKGROUND_READER = "background-slots"
INPUT_READER = "input-slots"
OUTPUT_READER = "output-slots"
key = ''
new = {}
data = {}
f1 = ''
inputSlots = []
outputSlots = []
hexColorForm = []


def main():
    start = time()
    functions = (
        translateInfo,
        translateGroups,
        translateMobDrops,
        translateGeoResources,
        translateItems,
        translateCapacitors,
        translateMachines,
        translateGenerators,
        translateSolarGenerators,
        translateMaterialGenerators,
        translateResearches
    )
    file_names = (
        'sc-addon.yml',
        'categories.yml',
        'mob-drops.yml',
        'geo-resources.yml',
        'items.yml',
        'capacitors.yml',
        'machines.yml',
        'generators.yml',
        'solar-generators.yml',
        'material-generators.yml',
        'researches.yml'
    )
    create_args_list = (
        (
            'info.yml', {
                'id': "RSC_SlimefunExpansion",
                'name': "Unknown addon",
                'depends': [],
                'pluginDepends': [],
                'version': "1.0 SNAPSHOT",
                'description': 'No description',
                'authors': [""],
                'repo': ''
            }
        ),
        'groups.yml',
        'mob_drops.yml',
        'geo_resources.yml',
        'items.yml',
        'capacitors.yml',
        'recipe_machines.yml',
        'generators.yml',
        'solar_generators.yml',
        'mat_generators.yml',
        'researches.yml'
    )
    yml_files = [
        file for file in os.listdir('.')
        if os.path.isfile(file)
        and file.endswith('.yml')
    ]
    try:
        if 'translate_config.yml' in yml_files:
            readConfig()
            generateBase()
            for funciton, file_name, create_args in zip(
                functions, file_names, create_args_list
            ):
                if file_name in yml_files:
                    funciton()
                else:
                    createFile(create_args)
            generateMenus()
            print(f'{Color.cyan}\nAs the author, I cannot guarantee that the translated text will be used, because the result will be affected by various factors.')
            print(f'{Color.cyan}Including but not limited to, the original configuration error, inconsistency, etc.')
            print(f"{Color.green}Done! {time()-start}")
        else:
            error('Cannot find translate_config.yml. Please complete the file from github and run the program again!')
    finally:
        error(f'\n{Color.red}If you encounter any problems, please submit an issue on the github repository.')
        error(f'{Color.red}Don\'t forget to change the id in info.yml before release.')
        input(f"{Color.cyan}Press any key to exit...{Color.red}")

if __name__ == '__main__':
    main()
    print(f'{Color.reset}')
