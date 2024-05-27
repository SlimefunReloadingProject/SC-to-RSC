import os
import re
import shutil
import sys
import yaml

from time import time

VERSION = '1.3-REALEASE'


class color:
    # Text color
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

    # Background color
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
    print(f'{color.red}{string}', end=end)


def loadingPrint(string, newline=False):
    sys.stdout.write('\r' + ' '*50)
    sys.stdout.write('\r' + string)
    if newline:
        sys.stdout.write('\n')
    sys.stdout.flush()


def getYamlContext(file):
    try:
        result = yaml.load(file, Loader=yaml.FullLoader)
        if result is None:
            return {}
        return result
    except FileNotFoundError:
        error(f'文件 {file} 未找到')
        return {}
    except PermissionError:
        error(f'无权限打开文件 {file}')
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
    order = (
        'id_alias',
        'lateinit',
        'register',
        'totalTicks',
        'type',
        'tier',
        'hidden',
        'protection_types',
        'fullSet',
        'item_group',
        'helmet',
        'chestplate',
        'leggings',
        'boots',
        'placeable',
        'item',
        'id',
        'material_type',
        'material',
        'name',
        'modelId',
        'glow',
        'lore',
        'amount',
        'script',
        'class',
        'arg_template',
        'args',
        'field',
        'method',
        'recipe_type',
        'recipe',
        'input',
        'output',
        'work',
        'sound',
        'max_deviation',
        'obtain_from_geo_miner',
        'geo_name',
        'entity',
        'chance',
        'supply',
        'world',
        'nether',
        'the_end',
        'energy_capacity',
        'radiation',
        'rainbow',
        'rainbow_materials',
        'anti_wither',
        'souldbound',
        'pinglin_trade_chance',
        'vanilla',
        'potion_effects',
        'energy',
        'settings',
        'capacity',
        'production',
        'title',
        'slots',
        'import',
        'fuels',
        'item',
        'seconds',
        'chooseOne',
        'dayEnergy',
        'nightEnergy',
        'lightLevel',
        'outputItem',
        'tickRate',
        'status',
        'per',
        'energyPerCraft',
        'consumption',
        'speed',
        'recipes',
        'levelCost',
        'currencyCost',
        'items',
        'drop_from',
        'drop_chance',
        'drop_amount'
    )
    try:
        return order.index(x[0])
    except ValueError:
        error(f'Unknown key: {x[0]}')
        return len(order)


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
            progressSlot = 22

        class generators:
            slots = {}
            inputSlots = []
            outputSlots = []
            progressSlot = 22

        class material_generators:
            slots = {}
            outputSlots = []
            progressSlot = 0

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
    if isinstance(slot, str):
        if slot == 'progress':
            return {'progressbar': True}
        return {'material': slot, 'name': '&a'}
    return slot


def readslot(slots, dt):
    current_slot = 0
    current_item = slots[0][0]
    clazz = getattr(config.menus, dt)
    length = len(slots)
    for line in range(length):
        for pos in range(9):
            apos = line*9+pos
            item = slots[line][pos]
            if item == 'i' and dt != 'material_generators':
                clazz.inputSlots.append(apos)
            elif item == 'o':
                clazz.outputSlots.append(apos)
            elif item == 'P':
                clazz.progressSlot = apos
            if item != current_item:
                if apos-1 == current_slot:
                    p = current_slot
                else:
                    p = f'{current_slot}-{apos-1}'
                if current_item not in 'ioN':
                    if (
                        dt != 'material_generators'
                        or (
                            dt == 'material_generators'
                            and current_item != 'P'
                        )
                    ):
                        clazz.slots[p] = encode(current_item)
                current_slot = apos
                current_item = item
    if apos == current_slot:
        p = current_slot
    else:
        p = f'{current_slot}-{apos}'
    if current_item not in 'ioN':
        clazz.slots[p] = encode(current_item)


def copyto(new_string, old_string, translate={}):
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
    # 能跑就行
    matches = re.findall(r'((&|§)x(((&|§)[0-9A-Fa-f]){6}))', item)
    if matches != []:
        for match in matches:
            code = match[0]
            temp = hexColorForm.format(
                code[3], code[5], code[7], code[9], code[11], code[13]
                )
            if config.colorMode == 'cmi':
                temp = '{' + temp + '}'
            item = item.replace(code, temp)

    for char in 'lmnok':
        while True:
            match1 = re.search(
                f'(&|§){char}((?!(&|§)).)*((&|§)(\d|[A-Fa-f]|#))?', item)
            if match1 is None:
                break
            match2 = match1.group()
            replace_char = None
            if match2[-1] in '0123456789abcdefABCDEF#':
                match2 = match2[:-1]
            if config.colorMode == 'minedown':
                charv = chars[char]
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
                charv = chars2[char]
                replace_char = match2.replace(f'&{char}', f'{charv}')
                item = item.replace(match2, replace_char)
            if replace_char is None:
                break
    return item


def copyName(key='item-name'):
    global new, data
    name = data[key]
    name = replaceColor(name)
    if 'item' not in new:
        new['item'] = {}
    new['item']['name'] = name


def copyLore(key='item-lore'):
    global new, data
    lores = data.get(key, [])
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
            copyto(
                f'recipe.{dkey}.material_type',
                f'crafting-recipe.{dkey}.type'
            )
            new['recipe'][int(dkey)]['material_type'] = 'none'
        if ct != "NONE":
            copyto(
                f'recipe.{dkey}.material_type',
                f'crafting-recipe.{dkey}.type', itemType
            )
            copyto(f'recipe.{dkey}.material', f'crafting-recipe.{dkey}.id')
            copyto(f'recipe.{dkey}.amount', f'crafting-recipe.{dkey}.amount')
            checkVersioned(ct, data['crafting-recipe'][dkey]['id'])


def copyRecipes():
    global new, data
    for dkey in data['recipes']:
        recipe = data['recipes'][dkey]
        copyto(
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
                    copyto(
                        f'{newPrefix}.material_type',
                        f'{oldPrefix}.type',
                        itemType
                    )
                    copyto(f'{newPrefix}.material', f'{oldPrefix}.id')
                    copyto(f'{newPrefix}.amount', f'{oldPrefix}.amount')


def copyRecipesGenerator():
    global new, data
    for dkey in data['recipes']:
        copyto(
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
            copyto(f'{newPrefix}.material_type', f'{oldPrefix}.type', itemType)
            copyto(f'{newPrefix}.material', f'{oldPrefix}.id')
            copyto(f'{newPrefix}.amount', f'{oldPrefix}.amount')
            item = new['fuels'][dkey]['item']
            checkVersioned(mt, item['material'])
        mt = data['recipes'][dkey]['output']['type']
        if mt != 'NONE' or (
            mt == 'VANILLA'
            and recipe['output']['id'].upper() != 'AIR'
        ):
            newPrefix = f"fuels.\"{dkey}\".output"
            oldPrefix = f"recipes.{dkey}.output"
            copyto(f'{newPrefix}.material_type', f'{oldPrefix}.type', itemType)
            copyto(f'{newPrefix}.material', f'{oldPrefix}.id')
            copyto(f'{newPrefix}.amount', f'{oldPrefix}.amount')
            item = new['fuels'][dkey]['output']
            checkVersioned(mt, item['material'])


def copyGroup():
    global new, data
    group = data['category']
    if "existing:" in group:
        split = group.split(':')
        new['item_group'] = f'outside:{split[1]}:{split[2]}'
    else:
        if config.groupMode == 'prefix':
            new['item_group'] = 'rsc_'+group
        elif config.groupMode == 'namespace':
            new['item_group'] = 'rykenslimecustomizer:'+group
        else:
            new['item_group'] = group


def ReadConfig():
    global hexColorForm
    with open('translate_config.yml', 'r', encoding='utf-8') as f:
        cfg = getYamlContext(f)
        config.outputFolder = cfg['outputFolder']
        config.colorMode = cfg['colorMode']
        config.groupMode = cfg['groupMode']
        config.setAllSaveditems_v = cfg['setAllSaveditems_v']
        menu = cfg['menus']
        cmenu = config.menus
        for section, value in menu['sections'].items():
            setattr(cmenu.sections, section, value)
        cmenu.machines.title = menu['machines']['title']
        cmenu.generators.title = menu['generators']['title']
        cmenu.material_generators.title = menu['material-generators']['title']
        readslot(menu['machines']['slots'], 'machines')
        readslot(menu['generators']['slots'], 'generators')
        readslot(menu['material-generators']['slots'], 'material_generators')
        config.lores.full_copy_slimecustomizer = cfg['lores'].get(
            'full-copy-slimecustomizer'
        )
        if config.lores.full_copy_slimecustomizer:
            print(f'''
                {color.cyan} 您已开启完全复制 SlimeCustomizer.
                在修改您的配置的时候请注意 lore 是否需要修改！
            ''')
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


def GenerateBase():
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
            shutil.copy(file_path, f"{config.outputFolder}/saveditems")
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
        "supers.yml"
    )
    for file_name in files:
        with open(getPath(file_name), 'w', encoding='utf-8') as f:
            f.write('\n')


def translateInfo():
    global new, data
    with open(getPath('info.yml'), 'w', encoding='utf-8') as f1:
        with open('sc-addon.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating sc-addon.yml')

            if config.info.enable:
                items = {
                    'id': config.info.id,
                    'name': config.info.name,
                    'depends': config.info.depends,
                    'pluginDepends': config.info.pluginDepends,
                    'version': config.info.version,
                    'description': config.info.description,
                    'authors': config.info.authors,
                    'repo': config.info.repo
                }
            else:
                items = {
                    'id': "RSC_SlimefunExpansion",
                    'name': "Unknown addon",
                    'depends': [],
                    'pluginDepends': [],
                    'version': "1.0 SNAPSHOT",
                    'description': 'No description',
                    'authors': [""],
                    'repo': ''
                }
            data = getYamlContext(f2)
            depend = data.get('depend', [])
            if 'Slimefun' in depend:
                depend.remove('Slimefun')
            items['pluginDepends'] = depend
            dump(f1, items)
    loadingPrint(f'{color.cyan}sc-addon.yml √', True)


def translateGroups():
    global new, data, needVersioned, f1, key
    with open(getPath('groups.yml'), 'w', encoding='utf-8') as f1:
        with open('categories.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating categories.yml')
            d = getYamlContext(f2)
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                if config.groupMode == 'prefix':
                    key = 'rsc_'+key
                new = items[key] = {}
                new['lateInit'] = False
                t = data.get('type', 'normal')
                # special check
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
                    new['item']['material'] = data['category-item'][5:]
                else:
                    copyto('item.material', 'category-item')
                checkVersioned(dtype, ditem)
                copyName('category-name')
                if t == 'sub':
                    cat = data['parent']
                    if "existing:" in cat:
                        split = cat.split(':')
                        new['parent'] = f'outside:{split[1]}:{split[2]}'
                    else:
                        if config.groupMode == 'prefix':
                            new['parent'] = 'rsc_'+cat
                        elif config.groupMode == 'namespace':
                            new['parent'] = 'rykenslimecustomizer:'+cat
                        else:
                            new['parent'] = cat
                elif t == 'seasonal':
                    copyto('month', 'month')
                elif t == 'locked':
                    copyto('parents', 'parents')
                if 'tier' in data:
                    copyto('tier', 'tier')
                # additions
                p = config.additions.categories
                loadAdditions(p, items, key)
                dump(f1, items)
                versionedObjectDump()
    loadingPrint(f'{color.cyan}categories.yml √', True)


def translateMobDrops():
    global new, data, needVersioned, f1, key
    with open(getPath('mob_drops.yml'), 'w', encoding='utf-8') as f1:
        with open('mob-drops.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating mob-drops.yml')
            d = getYamlContext(f2)
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
                    new['item']['material'] = data['item-id'][5:]
                else:
                    copyto('item.material_type', 'item-type', defineType)
                    copyto('item.material', 'item-id')
                copyto('item.amount', 'item-amount')

                copyto('entity', 'mob')
                copyto('chance', 'chance')
                # additions
                p = config.additions.mob_drops
                loadAdditions(p, items, key)
                dump(f1, items)
                versionedObjectDump()
    loadingPrint(f'{color.cyan}mob-drops.yml √', True)


def translateGeoResources():
    global new, data, needVersioned, f1, key
    with open(getPath('geo_resources.yml'), 'w', encoding='utf-8') as f1:
        with open('geo-resources.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating geo-resources.yml')
            d = getYamlContext(f2)
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
                    new['item']['material'] = data['item-id'][5:]
                else:
                    copyto('item.material_type', 'item-type', defineType)
                    copyto('item.material', 'item-id')
                checkVersioned(dtype, ditem)
                copyto('max_deviation', 'max-deviation')
                copyto('geo_name', 'item-name')
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
                # additions
                p = config.additions.geo_resources
                loadAdditions(p, items, key)
                dump(f1, items)
                versionedObjectDump()
    loadingPrint(f'{color.cyan}geo-resources.yml √', True)


def translateItems():
    global new, data, needVersioned, f1, key
    with open(getPath('items.yml'), 'w', encoding='utf-8') as f1:
        with open('items.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating items.yml')
            d = getYamlContext(f2)
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
                    new['item']['material'] = data['item-id'][5:]
                else:
                    copyto('item.material_type', 'item-type', defineType)
                    copyto('item.material', 'item-id')
                checkVersioned(dt, ditem)
                copyto('item.amount', 'item-amount')
                copyto('placeable', 'placeable', {NULL: False})
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                # additions
                p = config.additions.items
                loadAdditions(p, items, key)
                dump(f1, items)
                versionedObjectDump()
    loadingPrint(f'{color.cyan}items.yml √', True)


def translateCapacitors():
    global new, data, needVersioned, f1, key
    with open(getPath('capacitors.yml'), 'w', encoding='utf-8') as f1:
        with open('capacitors.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating capacitors.yml')
            d = getYamlContext(f2)
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
                        f"&8⇨ &e⚡&7 {data['capacity']} J 可存储",
                    ]
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                elif data['block-type'] in ('DEFAULT', 'default'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    new['item']['material'] = capaSkull
                else:
                    copyto('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                copyto('item.amount', 'item-amount')

                copyto('capacity', 'capacity')
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                # additions
                p = config.additions.capacitors
                loadAdditions(p, items, key)
                dump(f1, items)
                versionedObjectDump()
    loadingPrint(f'{color.cyan}capacitors.yml √', True)


def translateMachines():
    global new, data, needVersioned, f1, key, inputSlots, outputSlots
    with open(getPath('recipe_machines.yml'), 'w', encoding='utf-8') as f1:
        inputSlots = config.menus.machines.inputSlots
        outputSlots = config.menus.machines.outputSlots
        with open('machines.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating machines.yml')
            d = getYamlContext(f2)
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                menus['machines'].append({
                    'iden': key,
                    'name': data['machine-name'],
                    'progress': data['progress-bar-item']
                })
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName('machine-name')
                copyLore('machine-lore')
                SCMachineLore = [
                    "&b机器",
                    f"&8⇨ &e⚡&7 {data['stats']['energy-buffer']} J 可存储",
                    f"&8⇨ &e⚡&7 {data['stats']['energy-consumption']*2} J/s",
                ]
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] += SCMachineLore
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                else:
                    copyto('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                new['speed'] = 1
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                copyto('capacity', 'stats.energy-buffer')
                copyto('energyPerCraft', 'stats.energy-consumption')
                copyRecipes()
                # additions
                p = config.additions.machines
                loadAdditions(p, items, key)
                dump(f1, items)
                f1.write(f'  input: {inputSlots}\n  output: {outputSlots}\n')
                versionedObjectDump(i=True, o=True)
    loadingPrint(f'{color.cyan}machines.yml √', True)


def translateGenerators():
    global new, data, needVersioned, f1, key, inputSlots, outputSlots
    with open(getPath('generators.yml'), 'w', encoding='utf-8') as f1:
        inputSlots = config.menus.machines.inputSlots
        outputSlots = config.menus.machines.outputSlots
        with open('generators.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating generators.yml')
            d = getYamlContext(f2)
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                menus['generators'].append({
                    'iden': key,
                    'name': data['generator-name'],
                    'progress': data['progress-bar-item']
                })
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName('generator-name')
                copyLore('generator-lore')
                SCGeneratorLore = [
                    "&a发电机",
                    f"&8⇨ &e⚡&7 {data['stats']['energy-buffer']} J 可存储",
                    f"&8⇨ &e⚡&7 {data['stats']['energy-production']*2} J/s",
                ]
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] += SCGeneratorLore
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                else:
                    copyto('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                copyto('capacity', 'stats.energy-buffer')
                copyto('production', 'stats.energy-production')
                copyRecipesGenerator()
                # additions
                p = config.additions.generators
                loadAdditions(p, items, key)
                dump(f1, items)
                f1.write(f"  input: {inputSlots}\n  output: {outputSlots}\n")
                versionedObjectDump(i=True, o=True)
    loadingPrint(f'{color.cyan}generators.yml √', True)


def translateSolarGenerators():
    global new, data, needVersioned, f1, key
    with open(getPath('solar_generators.yml'), 'w', encoding='utf-8') as f1:
        with open('solar-generators.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating solar-generators.yml')
            d = getYamlContext(f2)
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = True
                copyGroup()
                copyName('generator-name')
                copyLore('generator-lore')
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                else:
                    copyto('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                new['lightLevel'] = 1
                dep = data['stats']['energy-production']
                de = dep['day']
                ne = dep['night']
                SCSolarGeneratorLore = [
                    "&e太阳能发电机",
                    f"&8⇨ &e⚡&7 {de*2} J/s (昼)",
                    f"&8⇨ &e⚡&7 {ne*2} J/s (夜)",
                ]
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] += SCSolarGeneratorLore
                new['dayEnergy'] = de
                new['nightEnergy'] = ne
                new['capacity'] = max(de, ne)
                # additions
                p = config.additions.solar_generators
                loadAdditions(p, items, key)
                dump(f1, items)
                versionedObjectDump()
    loadingPrint(f'{color.cyan}solar-generators.yml √', True)


def translateMaterialGenerators():
    global new, data, needVersioned, f1, key, outputSlots
    with open(getPath('mat_generators.yml'), 'w', encoding='utf-8') as f1:
        with open('material-generators.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating material-generators.yml')
            d = getYamlContext(f2)
            outputSlots = config.menus.material_generators.outputSlots
            progressSlot = config.menus.material_generators.progressSlot
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                menus['material-generators'].append({
                    'iden': key,
                    'name': data['item-name']
                })
                new = items[key] = {}
                new['lateInit'] = True
                copyGroup()
                copyName()
                copyLore()
                SCMaterialGeneratorLore = [
                    "&e材料生成器",
                    f"&8⇨ &7速度: &b每 {data['output']['tick-rate']} 粘液刻生成一次",
                    f"&8⇨ &e⚡&7 {data['stats']['energy-buffer']} J 可存储",
                    f"&8⇨ &e⚡&7 {data['stats']['energy-consumption']*2} J/s",
                ]
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] += SCMaterialGeneratorLore
                dtype = 'mc'
                ditem = data['block-type']
                if ditem.startswith('SKULL'):
                    new['item']['material_type'] = dtype = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                else:
                    copyto('item.material', 'block-type')
                checkVersioned(dtype, ditem)
                copyto('capacity', 'stats.energy-buffer')
                copyto('per', 'stats.energy-consumption')
                copyto('item.amount', 'item-amount')
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                new['status'] = progressSlot
                copyto('tickRate', 'output.tick-rate')
                if (
                    data['output']['type'] == 'VANILLA'
                    and data['output']['id'].upper() == 'AIR'
                ):
                    new['outputItem'] = {}
                    new['outputItem']['material_type'] = 'none'
                else:
                    copyto('outputItem.material_type', 'output.type', itemType)
                    copyto('outputItem.material', 'output.id')
                    copyto('outputItem.amount', 'output.amount')
                    checkVersioned(
                        new['outputItem']['material_type'],
                        new['outputItem']['material']
                    )
                # additions
                p = config.additions.material_generators
                loadAdditions(p, items, key)
                dump(f1, items)
                f1.write(f"  output: {outputSlots}\n")
                versionedObjectDump(o=True)
    loadingPrint(f'{color.cyan}material-generators.yml √', True)


def translateResearches():
    global new, data, needVersioned, f1, key
    with open(getPath('researches.yml'), 'w', encoding='utf-8') as f1:
        with open('researches.yml', 'r', encoding='utf-8') as f2:
            loadingPrint(f'{color.cyan}Translating researches.yml')
            d = getYamlContext(f2)
            for key in d:
                needVersioned = False
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = True
                copyto('id', 'id')
                copyto('name', 'name')
                copyto('levelCost', 'cost')
                copyto('items', 'items')
                # additions
                p = config.additions.researches
                loadAdditions(p, items, key)
                dump(f1, items)
                versionedObjectDump()
    loadingPrint(f'{color.cyan}researches.yml √', True)


def translateMenus():
    global new, data, needVersioned, f1, key
    with open(getPath('menus.yml'), 'w', encoding='utf-8') as f1:
        loadingPrint(f'{color.cyan}Generating meuns.yml')
        cfg = config.menus.machines
        progressSlot = cfg.progressSlot
        for menu in menus['machines']:
            items = {}
            iden = menu['iden']
            name = menu['name']
            progress_item = menu['progress']
            items[iden] = {
                "title": replaceColor(cfg.title.replace('%name%', name)),
                "slots": cfg.slots
            }
            items[iden]['slots'][progressSlot]['material'] = progress_item
            dump(f1, items)
        cfg = config.menus.generators
        progressSlot = cfg.progressSlot
        for menu in menus['generators']:
            items = {}
            iden = menu['iden']
            name = menu['name']
            progress_item = menu['progress']
            items[iden] = {
                "title": replaceColor(cfg.title.replace('%name%', name)),
                "slots": cfg.slots
            }
            items[iden]['slots'][cfg.progressSlot]['material'] = progress_item
            dump(f1, items)
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
    loadingPrint(f'{color.cyan}meuns.yml √', True)


def CreateFile(file_name, text=''):
    if isinstance(file_name, tuple):
        text = file_name[1]
        file_name = file_name[0]
    with open(getPath(file_name), 'w', encoding='utf-8') as f:
        f.write(f'\n{text}')
        loadingPrint(f'{color.green}{file_name} √', True)


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
capaSkull = '91361e576b493cbfdfae328661cedd1add55fab4e5eb418b92cebf6275f8bb4'
chars = {'n': '__', 'm': '~~', 'k': '??', 'l': '**', 'o': '##'}
chars2 = {'l': '<l>', 'n': '<u>', 'o': '<i>', 'k': '<obf>', 'm': '<st>'}
NULL = '__SC_TO_RSC_NOT_FOUND_ARG'
key = ''
new = {}
data = {}
f1 = ''
inputSlots = []
outputSlots = []
hexColorForm = []


def main():
    start = time()
    functions = [
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
    ]
    fileNames = [
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
    ]
    createArgsList = [
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
    ]
    yml_files = [
        file for file in os.listdir('.')
        if os.path.isfile(file)
        and file.endswith('.yml')
        ]
    try:
        if 'translate_config.yml' in yml_files:
            ReadConfig()
            GenerateBase()
            for funciton, fileName, createArgs in zip(
                functions, fileNames, createArgsList
            ):
                if fileName in yml_files:
                    funciton()
                else:
                    CreateFile(createArgs)
            translateMenus()
            print(f'{color.cyan}\n作为作者，我并不能保证转换出来的文本一定能够使用，因为结果会受到各种因素的影响')
            print(f'{color.cyan}包括但不限于，原配置错误，规则不一致等。')
            input(f"{color.cyan}Press Enter to exit...{color.red}")
        else:
            error('未找到配置文件 translate_config.yml. 请从github补全文件再运行本程序！')
    finally:
        error(f'\n{color.red}如遇无法转换，可能是配置不完整，如确认配置文件无误请提issue！')
        error(f'{color.red}记得修改 info.yml 以避免出现附属重名')
        print(f"{color.green}Spent {time()-start}")


if __name__ == '__main__':
    main()
