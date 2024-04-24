import argparse
import os
import re
import shutil
import yaml

from time import time

VERSION = '1.1REALEASE'


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


def error(string):
    print(f'{color.red}{string}')


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


class CombinedDumper(yaml.Dumper):
    def __init__(self, *args, **kwargs):
        super(CombinedDumper, self).__init__(*args, **kwargs)
        self.sort_keys = lambda x: x  # Override the default sorting behavior

    def ignore_aliases(self, data):
        return True

    def represent_list(self, data):
        return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

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
            if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
                best_style = False
            if not (isinstance(node_value, yaml.ScalarNode) and not node_value.style):
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


def custom_sort(x):
    order = (
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
        'recipe_type',
        'recipe',
        'input',
        'output',
        'work',
        'sound'
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
        'piglin_trade',
        'pinglin_trade_chance',
        'vanilla',
        'potion_effects',
        'energy',
        'settings'
        'capacity',
        'production'
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
        'consumption'
        'speed',
        'recipes',
        'levelCost',
        'currencyCost',
        'items'
    )
    try:
        return order.index(x[0])
    except ValueError:
        error(f'未知键: {x[0]}')
        return len(order)


def dump(file, item):
    yaml.dump(
        item,
        file,
        allow_unicode=True,
        encoding='utf-8',
        Dumper=CombinedDumper,
        sort_keys=custom_sort,
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


def encode(item):
    slot = getattr(config.menus.sections, item)
    if isinstance(slot, str):
        if slot == 'progress':
            return {'progressbar': True}
        return {'material': slot}
    return slot


def readslot(slots, dt):
    current_slot = 0
    current_item = slots[0][0]
    length = len(slots)
    for line in range(length):
        for pos in range(9):
            apos = line*9+pos
            item = slots[line][pos]
            if item == 'i' and dt != 'material_generators':
                getattr(config.menus, dt).inputSlots.append(apos)
            elif item == 'o':
                getattr(config.menus, dt).outputSlots.append(apos)
            elif item == 'P':
                getattr(config.menus, dt).progressSlot = apos
            if item != current_item:
                if apos-1 == current_slot:
                    p = current_slot
                else:
                    p = f'{current_slot}-{apos-1}'
                if current_item not in 'ioN':
                    if dt != 'material_generators' or (dt == 'material_generators' and current_item != 'P'):
                        getattr(config.menus, dt).slots[p] = encode(current_item)
                current_slot = apos
                current_item = item
    if apos == current_slot:
        p = current_slot
    else:
        p = f'{current_slot}-{apos}'
    if current_item not in 'ioN':
        getattr(config.menus, dt).slots[p] = encode(current_item)


def copyto(new_string, old_string, translate={}):
    global new, data
    new_split1 = new_string.split('.')
    old_split1 = old_string.split('.')

    new_split = []
    for a in new_split1:
        try:
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
                odat = null
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
    matches = re.findall(r'((&|§)x(((&|§)[0-9A-Fa-f]){6}))', item)
    if matches != []:
        for match in matches:
            code = match[0]
            item = item.replace(code, f'&#{code[3]}{code[5]}{code[7]}{code[9]}{code[11]}{code[13]}&')

    chars = {'n': '__', 'm': '~~', 'k': '??', 'l': '**', 'o': '##'}
    for char, charv in chars.items():
        while True:
            match = re.search(f'(&|§){char}((?!(&|§)).)*((&|§)(\d|[A-Fa-f]|#))?', item)
            if match is None:
                break
            match = match.group()
            if match[-1] in '0123456789abcdefABCDEF#':
                match = match[:-1]
            replace_char = match.replace(f'&{char}', f'{charv}')
            if match[-1] == '&':
                replace_char = replace_char.replace('&', f'{charv}&')
            elif match[-1] == '§':
                replace_char = replace_char.replace('§', f'{charv}§')
            else:
                replace_char += charv
            item = item.replace(match, replace_char)
            item = item.replace(charv*2, charv)
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
        copyto(f'recipe.{dkey}.material_type', f'crafting-recipe.{dkey}.type', itemtype)
        ct = data['crafting-recipe'][dkey]['type']
        if ct != 'NONE':
            copyto(f'recipe.{dkey}.material', f'crafting-recipe.{dkey}.id')
            copyto(f'recipe.{dkey}.amount', f'crafting-recipe.{dkey}.amount')


def copyRecipes(isGenerator=False):
    global new, data
    for dkey in data['recipes']:
        if not isGenerator:
            recipe = data['recipes'][dkey]
            copyto(f'recipes.\"{dkey}\".seconds', f'recipes.{dkey}.speed-in-seconds', {0: 1})
            mt = recipe['input']['1']['type'] if '1' in recipe['input'] else recipe['input'][1]['type']
            if mt != 'NONE':
                copyto(f'recipes.\"{dkey}\".input.1.material_type', f'recipes.{dkey}.input.1.type', itemtype)
                copyto(f'recipes.\"{dkey}\".input.1.material', f'recipes.{dkey}.input.1.id')
                copyto(f'recipes.\"{dkey}\".input.1.amount', f'recipes.{dkey}.input.1.amount')
            mt = data['recipes'][dkey]['output']['1']['type'] if '1' in recipe['output'] else recipe['output'][1]['type']
            if mt != 'NONE':
                copyto(f'recipes.\"{dkey}\".output.1.material_type', f'recipes.{dkey}.output.1.type', itemtype)
                copyto(f'recipes.\"{dkey}\".output.1.material', f'recipes.{dkey}.output.1.id')
                copyto(f'recipes.\"{dkey}\".output.1.amount', f'recipes.{dkey}.output.1.amount')
            mt = data['recipes'][dkey]['input']['2']['type'] if '2' in recipe['input'] else recipe['input'][2]['type']
            if mt != 'NONE':
                copyto(f'recipes.\"{dkey}\".input.2.material_type', f'recipes.{dkey}.input.2.type', itemtype)
                copyto(f'recipes.\"{dkey}\".input.2.material', f'recipes.{dkey}.input.2.id')
                copyto(f'recipes.\"{dkey}\".input.2.amount', f'recipes.{dkey}.input.2.amount')
            mt = data['recipes'][dkey]['output']['2']['type'] if '2' in recipe['output'] else recipe['output'][2]['type']
            if mt != 'NONE':
                copyto(f'recipes.\"{dkey}\".output.2.material_type', f'recipes.{dkey}.output.2.type', itemtype)
                copyto(f'recipes.\"{dkey}\".output.2.material', f'recipes.{dkey}.output.2.id')
                copyto(f'recipes.\"{dkey}\".output.2.amount', f'recipes.{dkey}.output.2.amount')
        else:
            copyto(f'fuels.\"{dkey}\".seconds', f'recipes.{dkey}.time-in-seconds', {0: 1})
            mt = data['recipes'][dkey]['input']['type']
            if mt != 'NONE':
                copyto(f'fuels.\"{dkey}\".item.material_type', f'recipes.{dkey}.input.type', itemtype)
                copyto(f'fuels.\"{dkey}\".item.material', f'recipes.{dkey}.input.id')
                copyto(f'fuels.\"{dkey}\".item.amount', f'recipes.{dkey}.input.amount')
            mt = data['recipes'][dkey]['input']['type']
            if mt != 'NONE':
                copyto(f'fuels.\"{dkey}\".output.material_type', f'recipes.{dkey}.output.type', itemtype)
                copyto(f'fuels.\"{dkey}\".output.material', f'recipes.{dkey}.output.id')
                copyto(f'fuels.\"{dkey}\".output.amount', f'recipes.{dkey}.output.amount')


def copyGroup():
    global new, data
    cat = data['category']
    if "existing:" in cat:
        new['item_group'] = cat.split(':')[2]
    else:
        new['item_group'] = 'rsc_'+cat


def ReadConfig():
    with open('translate_config.yml', 'r', encoding='utf-8') as f:
        c = getYamlContext(f)
        config.outputFolder = c['outputFolder']
        menu = c['menus']
        for section, value in menu['sections'].items():
            setattr(config.menus.sections, section, value)
        config.menus.machines.title = menu['machines']['title']
        config.menus.generators.title = menu['generators']['title']
        config.menus.material_generators.title = menu['material-generators']['title']
        readslot(menu['machines']['slots'], 'machines')
        readslot(menu['generators']['slots'], 'generators')
        readslot(menu['material-generators']['slots'], 'material_generators')
        config.lores.full_copy_slimecustomizer = c['lores']['full-copy-slimecustomizer']
        if config.lores.full_copy_slimecustomizer:
            print(f'{color.cyan} 您已开启完全复制 SlimeCustomizer. 在修改您的配置的时候请注意 lore 是否需要修改！')


def GenerateBase():
    folders = (f"{config.outputFolder}", f"{config.outputFolder}/saveditems", f"{config.outputFolder}/scripts")
    for folder in folders:
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass

    for file_name in os.listdir("saveditems"):
        file_path = os.path.join("saveditems", file_name)
        if os.path.isfile(file_path):
            shutil.copy(file_path, f"{config.outputFolder}/saveditems")

    with open(f'{config.outputFolder}/machines.yml', 'w', encoding='utf-8') as f:
        f.write('\n')
    with open(f'{config.outputFolder}/simple_machines.yml', 'w', encoding='utf-8') as f:
        f.write('\n')
    with open(f'{config.outputFolder}/mb_machines.yml', 'w', encoding='utf-8') as f:
        f.write('\n')
    with open(f'{config.outputFolder}/armors.yml', 'w', encoding='utf-8') as f:
        f.write('\n')
    with open(f'{config.outputFolder}/recipe_types.yml', 'w', encoding='utf-8') as f:
        f.write('\n')


def translateInfo():
    global new, data
    with open(f'{config.outputFolder}/info.yml', 'w', encoding='utf-8') as f1:
        with open('sc-addon.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating sc-addon.yml')
            parser = argparse.ArgumentParser()
            parser.add_argument('--id', type=str, required=False)
            parser.add_argument('--name', type=str, required=False)
            parser.add_argument('--version', type=str, required=False)
            parser.add_argument('--description', type=str, required=False)
            args = parser.parse_args()

            items = {
                'id': "RSC_SlimefunExpansion" if args.id is None else args.id,
                'name': "Unknown addon" if args.name is None else args.name,
                'depends': [],
                'pluginDepends': [],
                'version': "1.0 SNAPSHOT" if args.version is None else args.version,
                'description': 'No description' if args.description is None else args.description,
                'authors': [""],
                'repo': ''
            }
            data = getYamlContext(f2)
            depend = data.get('depend', [])
            if 'Slimefun' in depend:
                depend.remove('Slimefun')
            items['pluginDepends'] = depend
            dump(f1, items)


def translateGroups():
    global new, data
    with open(f'{config.outputFolder}/groups.yml', 'w', encoding='utf-8') as f1:
        with open('categories.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating categories.yml')
            d = getYamlContext(f2)
            for key in d:
                items = {}
                data = d[key]
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
                if data['category-item'].startswith('SKULL'):
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = data['category-item'][5:]
                else:
                    copyto('item.material', 'category-item')
                copyName('category-name')
                if t == 'sub':
                    cat = data['parent']
                    if "existing:" in cat:
                        new['parent'] = cat.split(':')[2]
                    else:
                        new['parent'] = 'rsc_'+cat
                elif t == 'seasonal':
                    copyto('month', 'month')
                elif t == 'locked':
                    copyto('parents', 'parents')
                if 'tier' in data:
                    copyto('tier', 'tier')
                dump(f1, items)


def translateMobDrops():
    global new, data
    with open(f'{config.outputFolder}/mob_drops.yml', 'w', encoding='utf-8') as f1:
        with open('mob-drops.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating mob-drops.yml')
            d = getYamlContext(f2)
            for key in d:
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName()
                copyLore()
                if data['item-id'].startswith('SKULL') and data['item-type'] == 'CUSTOM':
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = data['item-id'][5:]
                else:
                    copyto('item.material_type', 'item-type', {'CUSTOM': 'mc', 'SAVEDITEM': 'saveditem'})
                    copyto('item.material', 'item-id')
                copyto('item.amount', 'item-amount')

                copyto('entity', 'mob')
                copyto('chance', 'chance')
                dump(f1, items)


def translateGeoResources():
    global new, data
    with open(f'{config.outputFolder}/geo_resources.yml', 'w', encoding='utf-8') as f1:
        with open('geo-resources.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating geo-resources.yml')
            d = getYamlContext(f2)
            for key in d:
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName()
                copyLore()
                if data['item-id'].startswith('SKULL') and data['item-type'] == 'CUSTOM':
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = data['item-id'][5:]
                else:
                    copyto('item.material_type', 'item-type', {'CUSTOM': 'mc', 'SAVEDITEM': 'saveditem'})
                    copyto('item.material', 'item-id')
                copyto('max_deviation', 'max-deviation')
                copyto('geo_name', 'item-name')
                new['recipe_type'] = 'GEO_MINER'
                new['obtain_from_geo_miner'] = True
                new['supply'] = {}
                new['supply']['normal'] = {}
                new['supply']['nether'] = {}
                new['supply']['the_end'] = {}
                biomes = data.get('biome', null)
                if biomes != null:
                    new['supply']['normal'] = biomes
                    new['supply']['nether'] = biomes
                    new['supply']['the_end'] = biomes
                envs = data.get('environment', null)
                if envs != null:
                    if new['supply']['normal'] == {}:
                        new['supply']['normal'] = envs.get('NORMAL', 0)
                    else:
                        new['supply']['normal']['others'] = envs.get('NORMAL', 0)
                    if new['supply']['nether'] == {}:
                        new['supply']['nether'] = envs.get('NETHER', 0)
                    else:
                        new['supply']['nether']['others'] = envs.get('NETHER', 0)
                    if new['supply']['the_end'] == {}:
                        new['supply']['the_end'] = envs.get('THE_END', 0)
                    else:
                        new['supply']['the_end']['others'] = envs.get('THE_END', 0)
                if new['supply']['normal'] == {}:
                    new['supply']['normal'] = 0
                if new['supply']['nether'] == {}:
                    new['supply']['nether'] = 0
                if new['supply']['the_end'] == {}:
                    new['supply']['the_end'] = 0
                dump(f1, items)


def translateItems():
    global new, data
    with open(f'{config.outputFolder}/items.yml', 'w', encoding='utf-8') as f1:
        with open('items.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating items.yml')
            d = getYamlContext(f2)
            for key in d:
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName()
                copyLore()
                if str(data['item-id']).startswith('SKULL') and data['item-type'] == 'CUSTOM':
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = data['item-id'][5:]
                else:
                    copyto('item.material_type', 'item-type', {'CUSTOM': 'mc', 'SAVEDITEM': 'saveditem'})
                    copyto('item.material', 'item-id')
                copyto('item.amount', 'item-amount')

                copyto('placeable', 'placeable')
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                dump(f1, items)


def translateCapacitors():
    global new, data
    with open(f'{config.outputFolder}/capacitors.yml', 'w', encoding='utf-8') as f1:
        with open('capacitors.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating capacitors.yml')
            d = getYamlContext(f2)
            for key in d:
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = False
                copyGroup()
                copyName('capacitor-name')
                copyLore('capacitor-lore')
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] = new['item']['lore']+[
                        "",
                        "&e电容",
                        f"&8⇨ &e⚡&7 {data['capacity']} J 可存储",
                    ]
                if data['block-type'].startswith('SKULL'):
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                elif data['block-type'] in ('DEFAULT', 'default'):
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = '91361e576b493cbfdfae328661cedd1add55fab4e5eb418b92cebf6275f8bb4'
                else:
                    copyto('item.material', 'block-type')
                copyto('item.amount', 'item-amount')

                copyto('capacity', 'capacity')
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                dump(f1, items)


def translateMachines():
    global new, data
    with open(f'{config.outputFolder}/recipe_machines.yml', 'w', encoding='utf-8') as f1:
        inputSlots = config.menus.machines.inputSlots
        outputSlots = config.menus.machines.outputSlots
        with open('machines.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating machines.yml')
            d = getYamlContext(f2)
            for key in d:
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
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] = new['item']['lore']+[
                        "",
                        "&b机器",
                        f"&8⇨ &e⚡&7 {data['stats']['energy-buffer']} J 可存储",
                        f"&8⇨ &e⚡&7 {data['stats']['energy-consumption']*2} J/s",
                    ]
                if data['block-type'].startswith('SKULL'):
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                else:
                    copyto('item.material', 'block-type')

                new['input'] = inputSlots
                new['output'] = outputSlots
                new['speed'] = 1
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                copyto('capacity', 'stats.energy-buffer')
                copyto('energyPerCraft', 'stats.energy-consumption')
                copyRecipes()
                dump(f1, items)


def translateGenerators():
    global new, data
    with open(f'{config.outputFolder}/generators.yml', 'w', encoding='utf-8') as f1:
        inputSlots = config.menus.machines.inputSlots
        outputSlots = config.menus.machines.outputSlots
        with open('generators.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating generators.yml')
            d = getYamlContext(f2)
            for key in d:
                items = {}
                data = d[key]
                menus['generators'].append({
                    'iden': key,
                    'name': data['generator-name'],
                    'progress': data['progress-bar-item']
                })
                new = items[key] = {}
                new['lateInit'] = True
                copyGroup()
                copyName('generator-name')
                copyLore('generator-lore')
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] = new['item']['lore']+[
                        "",
                        "&a发电机",
                        f"&8⇨ &e⚡&7 {data['stats']['energy-buffer']} J 可存储",
                        f"&8⇨ &e⚡&7 {data['stats']['energy-production']*2} J/s",
                    ]
                if data['block-type'].startswith('SKULL'):
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                else:
                    copyto('item.material', 'block-type')

                new['input'] = inputSlots
                new['output'] = outputSlots
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                copyto('capacity', 'stats.energy-buffer')
                copyto('production', 'stats.energy-production')
                copyRecipes(isGenerator=True)
                dump(f1, items)


def translateSolarGenerators():
    global new, data
    with open(f'{config.outputFolder}/solar_generators.yml', 'w', encoding='utf-8') as f1:
        with open('solar-generators.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating solar-generators.yml')
            d = getYamlContext(f2)
            for key in d:
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = True
                copyGroup()
                copyName('generator-name')
                copyLore('generator-lore')
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] = new['item']['lore']+[
                        "",
                        "&e太阳能发电机",
                        f"&8⇨ &e⚡&7 {data['stats']['energy-production']['day']*2} J/s (昼)",
                        f"&8⇨ &e⚡&7 {data['stats']['energy-production']['night']*2} J/s (夜)",
                    ]
                if data['block-type'].startswith('SKULL'):
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                else:
                    copyto('item.material', 'block-type')

                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                new['lightLevel'] = 1
                de = data['stats']['energy-production']['day']
                ne = data['stats']['energy-production']['night']
                new['dayEnergy'] = de
                new['nightEnergy'] = ne
                new['capacity'] = max(de, ne)

                dump(f1, items)


def translateMaterialGenerators():
    global new, data
    with open(f'{config.outputFolder}/mat_generators.yml', 'w', encoding='utf-8') as f1:
        with open('material-generators.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating material-generators.yml')
            d = getYamlContext(f2)
            outputSlots = config.menus.material_generators.outputSlots
            progressSlot = config.menus.material_generators.progressSlot
            for key in d:
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
                if config.lores.full_copy_slimecustomizer:
                    new['item']['lore'] = new['item']['lore']+[
                        "",
                        "&e材料生成器",
                        f"&8⇨ &7速度: &b每 {data['output']['tick-rate']} 粘液刻生成一次",
                        f"&8⇨ &e⚡&7 {data['stats']['energy-buffer']} J 可存储",
                        f"&8⇨ &e⚡&7 {data['stats']['energy-consumption']*2} J/s",
                    ]
                if data['block-type'].startswith('SKULL'):
                    new['item']['material_type'] = 'skull_hash'
                    new['item']['material'] = data['block-type'][5:]
                else:
                    copyto('item.material', 'block-type')

                copyto('capacity', 'stats.energy-buffer')
                copyto('per', 'stats.energy-consumption')
                copyto('item.amount', 'item-amount')
                copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
                copyRecipe()
                new['output'] = outputSlots
                new['status'] = progressSlot
                copyto('tickRate', 'output.tick-rate')
                copyto('outputItem.material_type', 'output.type', itemtype)
                copyto('outputItem.material', 'output.id')
                copyto('outputItem.amount', 'output.amount')
                dump(f1, items)


def translateResearches():
    global new, data
    with open(f'{config.outputFolder}/researches.yml', 'w', encoding='utf-8') as f1:
        with open('researches.yml', 'r', encoding='utf-8') as f2:
            print(f'{color.cyan}Translating researches.yml')
            d = getYamlContext(f2)
            for key in d:
                items = {}
                data = d[key]
                new = items[key] = {}
                new['lateInit'] = True
                copyto('id', 'id')
                copyto('name', 'name')
                copyto('levelCost', 'cost')
                copyto('items', 'items')
                dump(f1, items)


def translateMenus():
    global new, data
    with open(f'{config.outputFolder}/menus.yml', 'w', encoding='utf-8') as f1:
        print(f'{color.cyan}Generating meuns.yml')
        items = {}
        progressSlot = config.menus.machines.progressSlot
        for menu in menus['machines']:
            items = {}
            iden = menu['iden']
            name = menu['name']
            progress_item = menu['progress']
            items[iden] = {
                "title": config.menus.machines.title.replace('%name%', name),
                "slots": config.menus.machines.slots
                }
            items[iden]['slots'][progressSlot]['material'] = progress_item
            dump(f1, items)
        for menu in menus['generators']:
            items = {}
            iden = menu['iden']
            name = menu['name']
            progress_item = menu['progress']
            items[iden] = {
                "title": config.menus.generators.title.replace('%name%', name),
                "slots": config.menus.generators.slots
                }
            items[iden]['slots'][config.menus.generators.progressSlot]['material'] = progress_item
            dump(f1, items)
        for menu in menus['material-generators']:
            items = {}
            iden = menu['iden']
            name = menu['name']
            items[iden] = {
                "title": config.menus.material_generators.title.replace('%name%', name),
                "slots": config.menus.material_generators.slots
            }
            dump(f1, items)


def CreateFile(file_name, text=''):
    with open(f'{config.outputFolder}/{file_name}', 'w', encoding='utf-8') as f:
        f.write(f'\n{text}')
        print(f'{color.green}已补全文件{file_name}')


menus = {'machines': [], 'generators': [], 'material-generators': []}
itemtype = {'VANILLA': 'mc', 'SLIMEFUN': 'slimefun', 'NONE': 'none', 'SAVEDITEM': 'saveditem'}
null = '__NOT_FOUND_SC_TO_RSC'


def main():
    start = time()
    yml_files = [file for file in os.listdir('.') if os.path.isfile(file) and file.endswith('.yml')]
    try:
        if 'translate_config.yml' in yml_files:
            ReadConfig()
            GenerateBase()
            translateInfo() if 'sc-addon.yml' in yml_files else CreateFile('info.yml', {'id': "RSC_SlimefunExpansion", 'name': "Unknown addon", 'depends': [], 'pluginDepends': [], 'version': "1.0 SNAPSHOT", 'description': 'No description', 'authors': [""], 'repo': ''})
            translateGroups() if 'categories.yml' in yml_files else CreateFile('groups.yml')
            translateMobDrops() if 'mob-drops.yml' in yml_files else CreateFile('mob_drops.yml')
            translateGeoResources() if 'geo-resources.yml' in yml_files else CreateFile('geo_resources.yml')
            translateItems() if 'items.yml' in yml_files else CreateFile('items.yml')
            translateCapacitors() if 'capacitors.yml' in yml_files else CreateFile('capacitors.yml')
            translateMachines() if 'machines.yml' in yml_files else CreateFile('recipe_machines.yml')
            translateGenerators() if 'generators.yml' in yml_files else CreateFile('generators.yml')
            translateSolarGenerators() if 'solar-generators.yml' in yml_files else CreateFile('solar_generators.yml')
            translateMaterialGenerators() if 'material-generators.yml' in yml_files else CreateFile('mat_generators.yml')
            translateResearches() if 'researches.yml' in yml_files else CreateFile('researches.yml')
            print(f'{color.cyan}作为作者，我并不能保证转换出来的文本一定能够使用，因为结果会受到各种因素的影响')
            print(f'{color.cyan}包括但不限于，原配置错误，规则更新。')
        else:
            error('未找到配置文件 translate_config.yml. 请从github补全文件再运行本程序！')
    except BaseException as err:
        error(f'无法转换文件！{err}')
        error('可能是配置不完整，如确认配置文件无误请提issue！')
    finally:
        print(f"{color.green}Spent {time()-start}")
        input(f"{color.cyan}Press Enter to exit...")


if __name__ == '__main__':
    main()
