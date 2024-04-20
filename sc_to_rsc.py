import argparse
import os
import re
import shutil
import yaml

from time import time

version = '1.0REALEASE'


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


def getYamlContext(file):
    try:
        result = yaml.load(file, Loader=yaml.FullLoader)
        if result is None:
            return {}
        return result
    except FileNotFoundError:
        print(f'{color.red}{file}未找到')
        return {}
    except PermissionError:
        print(f'{color.red}无权限')
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
    order = [
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
    ]
    try: 
        return order.index(x[0])
    except ValueError:
        print(x[0])
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


start = time()
menus = {'machines': [], 'generators': [], 'material-generators': []}
itemtype = {'VANILLA': 'mc', 'SLIMEFUN': 'slimefun', 'NONE': 'none', 'SAVEDITEM': 'saveditem'}
null = 'NOT_FOUND'


folders = ("translated", "translated/saveditems", "translated/scripts")
for folder in folders:
    try:
        os.mkdir(folder)
    except FileExistsError:
        1

saveditems_path = "saveditems"

for file_name in os.listdir(saveditems_path):
    file_path = os.path.join(saveditems_path, file_name)
    if os.path.isfile(file_path):
        shutil.copy(file_path, "translated/saveditems")

with open('translated/machines.yml', 'w', encoding='utf-8') as f: f.write('\n')
with open('translated/simple_machines.yml', 'w', encoding='utf-8') as f: f.write('\n')
with open('translated/mb_machines.yml', 'w', encoding='utf-8') as f: f.write('\n')
with open('translated/armors.yml', 'w', encoding='utf-8') as f: f.write('\n')
with open('translated/recipe_types.yml', 'w', encoding='utf-8') as f: f.write('\n')

with open('translated/info.yml', 'w', encoding='utf-8') as f1:
    with open('sc-addon.yml', 'r', encoding='utf-8') as f2:
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


def copyto(new_string, old_string, translate={}):
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
            if match == None:
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
    name = data[key]
    name = replaceColor(name)
    if 'item' not in new:
        new['item'] = {}
    new['item']['name'] = name


def copyLore(key='item-lore'):
    lores = data.get(key, [])
    new_lores = []
    if isinstance(lores, list):
        for lore in lores:
            new_lores.append(replaceColor(lore))
            #new_lores.append(lore)
    if 'item' not in new:
        new['item'] = {}
    new['item']['lore'] = new_lores


def copyRecipe():
    for dkey in data['crafting-recipe']:
        copyto(f'recipe.{dkey}.material_type', f'crafting-recipe.{dkey}.type', itemtype)
        ct = data['crafting-recipe'][dkey]['type']
        if ct != 'NONE':
            copyto(f'recipe.{dkey}.material', f'crafting-recipe.{dkey}.id')
            copyto(f'recipe.{dkey}.amount', f'crafting-recipe.{dkey}.amount')


def copyRecipes(isGenerator=False):
    for dkey in data['recipes']:
        if not isGenerator:
            copyto(f'recipes.\"{dkey}\".seconds', f'recipes.{dkey}.speed-in-seconds', {0: 1})
            mt = data['recipes'][dkey]['input']['1']['type']
            if mt != 'NONE':
                copyto(f'recipes.\"{dkey}\".input.1.material_type', f'recipes.{dkey}.input.1.type', itemtype)
                copyto(f'recipes.\"{dkey}\".input.1.material', f'recipes.{dkey}.input.1.id')
                copyto(f'recipes.\"{dkey}\".input.1.amount', f'recipes.{dkey}.input.1.amount')
            mt = data['recipes'][dkey]['output']['1']['type']
            if mt != 'NONE':
                copyto(f'recipes.\"{dkey}\".output.1.material_type', f'recipes.{dkey}.output.1.type', itemtype)
                copyto(f'recipes.\"{dkey}\".output.1.material', f'recipes.{dkey}.output.1.id')
                copyto(f'recipes.\"{dkey}\".output.1.amount', f'recipes.{dkey}.output.1.amount')
            mt = data['recipes'][dkey]['input']['2']['type']
            if mt != 'NONE':
                copyto(f'recipes.\"{dkey}\".input.2.material_type', f'recipes.{dkey}.input.2.type', itemtype)
                copyto(f'recipes.\"{dkey}\".input.2.material', f'recipes.{dkey}.input.2.id')
                copyto(f'recipes.\"{dkey}\".input.2.amount', f'recipes.{dkey}.input.2.amount')
            mt = data['recipes'][dkey]['output']['2']['type']
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
    cat = data['category']
    if "existing:" in cat:
        new['item_group'] = cat.split(':')[2]
    else:
        new['item_group'] = 'rsc_'+cat


with open('translated/groups.yml', 'w', encoding='utf-8') as f1:
    with open('categories.yml', 'r', encoding='utf-8') as f2:
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


with open('translated/mob_drops.yml', 'w', encoding='utf-8') as f1:
    with open('mob-drops.yml', 'r', encoding='utf-8') as f2:
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
            copyto('chance', 'chance', {0: 1})
            dump(f1, items)


with open('translated/geo_resources.yml', 'w', encoding='utf-8') as f1:
    with open('geo-resources.yml', 'r', encoding='utf-8') as f2:
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
            biomes = data.get('biome', null)
            new['supply']['world'] = {}
            new['supply']['nether'] = {}
            new['supply']['the_end'] = {}
            if biomes != null:
                new['supply']['world'] = biomes
                new['supply']['nether'] = biomes
                new['supply']['the_end'] = biomes
            envs = data.get('environment', null)
            if envs != null:
                new['supply']['world']['others'] = envs.get('NORMAL', 0)
                new['supply']['nether']['others'] = envs.get('NETHER', 0)
                new['supply']['the_end']['others'] = envs.get('THE_END', 0)
            dump(f1, items)
with open('translated/items.yml', 'w', encoding='utf-8') as f1:
    with open('items.yml', 'r', encoding='utf-8') as f2:
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

with open('translated/capacitors.yml', 'w', encoding='utf-8') as f1:
    with open('capacitors.yml', 'r', encoding='utf-8') as f2:
        d = getYamlContext(f2)
        for key in d:
            items = {}
            data = d[key]
            new = items[key] = {}
            new['lateInit'] = False
            copyGroup()
            copyName('capacitor-name')
            copyLore('capacitor-lore')
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

with open('translated/recipe_machines.yml', 'w', encoding='utf-8') as f1:
    with open('machines.yml', 'r', encoding='utf-8') as f2:
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
            if data['block-type'].startswith('SKULL'):
                new['item']['material_type'] = 'skull_hash'
                new['item']['material'] = data['block-type'][5:]
            else:
                copyto('item.material', 'block-type')

            new['input'] = [19, 20]
            new['output'] = [24, 25]
            new['speed'] = 1
            copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
            copyRecipe()
            copyto('capacity', 'stats.energy-buffer')
            copyto('energyPerCraft', 'stats.energy-consumption')
            copyRecipes()
            dump(f1, items)

with open('translated/generators.yml', 'w', encoding='utf-8') as f1:
    with open('generators.yml', 'r', encoding='utf-8') as f2:
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
            new['lateInit'] = False
            copyGroup()
            copyName('generator-name')
            copyLore('generator-lore')
            if data['block-type'].startswith('SKULL'):
                new['item']['material_type'] = 'skull_hash'
                new['item']['material'] = data['block-type'][5:]
            else:
                copyto('item.material', 'block-type')

            new['input'] = [19, 20]
            new['output'] = [24, 25]
            copyto('recipe_type', 'crafting-recipe-type', {"NONE": "NULL"})
            copyRecipe()
            copyto('capacity', 'stats.energy-buffer')
            copyto('production', 'stats.energy-production')
            copyRecipes(isGenerator=True)
            dump(f1, items)

with open('translated/solar_generators.yml', 'w', encoding='utf-8') as f1:
    with open('solar-generators.yml', 'r', encoding='utf-8') as f2:
        d = getYamlContext(f2)
        for key in d:
            items = {}
            data = d[key]
            new = items[key] = {}
            new['lateInit'] = False
            copyGroup()
            copyName('generator-name')
            copyLore('generator-lore')
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

with open('translated/mat_generators.yml', 'w', encoding='utf-8') as f1:
    with open('material-generators.yml', 'r', encoding='utf-8') as f2:
        d = getYamlContext(f2)
        for key in d:
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
            new['output'] = [2, 3, 4, 5, 6, 7]
            new['status'] = 0
            copyto('tickRate', 'output.tick-rate')
            copyto('outputItem.material_type', 'output.type', itemtype)
            copyto('outputItem.material', 'output.id')
            copyto('outputItem.amount', 'output.amount')
            dump(f1, items)

with open('translated/researches.yml', 'w', encoding='utf-8') as f1:
    with open('researches.yml', 'r', encoding='utf-8') as f2:
        d = getYamlContext(f2)
        for key in d:
            items = {}
            data = d[key]
            new = items[key] = {}
            new['lateInit'] = False
            copyto('id', 'id')
            copyto('name', 'name')
            copyto('levelCost', 'cost')
            copyto('items', 'items')
            dump(f1, items)

with open('translated/menus.yml', 'w', encoding='utf-8') as f1:
    items = {}
    for menu in menus['machines']+menus['generators']:
        iden = menu['iden']
        name = menu['name']
        progress_item = menu['progress']
        items[iden] = {
            "title": name,
            "slots": {
                "0-8": {
                    "name": "&a",
                    "material": "GRAY_STAINED_GLASS_PANE"
                },
                "9-12": {
                    "name": "&a",
                    "material": "BLUE_STAINED_GLASS_PANE"
                },
                13: {
                    "name": "&a",
                    "material": "GRAY_STAINED_GLASS_PANE"
                },
                "14-17": {
                    "name": "&a",
                    "material": "ORANGE_STAINED_GLASS_PANE"
                },
                18: {
                    "name": "&a",
                    "material": "BLUE_STAINED_GLASS_PANE"
                },
                21: {
                    "name": "&a",
                    "material": "BLUE_STAINED_GLASS_PANE"
                },
                22: {
                    "name": "&a",
                    "material": progress_item,
                    "progessbar": True
                },
                23: {
                    "name": "&a",
                    "material": "ORANGE_STAINED_GLASS_PANE"
                },
                26: {
                    "name": "&a",
                    "material": "ORANGE_STAINED_GLASS_PANE"
                },
                "27-30": {
                    "name": "&a",
                    "material": "BLUE_STAINED_GLASS_PANE"
                },
                31: {
                    "name": "&a",
                    "material": "GRAY_STAINED_GLASS_PANE"
                },
                "32-35": {
                    "name": "&a",
                    "material": "ORANGE_STAINED_GLASS_PANE"
                },
                "36-44": {
                    "name": "&a",
                    "material": "GRAY_STAINED_GLASS_PANE"
                }
            }
        }
    for menu in menus['material-generators']:
        iden = menu['iden']
        name = menu['name']
        items[iden] = {
            "title": name,
            "slots": {
                1: {
                    "name": "&a",
                    "material": "ORANGE_STAINED_GLASS_PANE"
                },
                8: {
                    "name": "&a",
                    "material": "ORANGE_STAINED_GLASS_PANE"
                }
            }
        }
    dump(f1, items)
print(f"{color.green}Spent {time()-start}")
