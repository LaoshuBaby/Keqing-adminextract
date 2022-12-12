import pprint
from typing import Dict, List

from kqs.waifu import Waifu


def show_hierarchy(relation_list: List[List[str]]) -> None:
    hierarchy: Dict[str, List[List[str]]] = {}
    for relation in relation_list:
        admin_level = relation[1]
        if hierarchy.get(admin_level) == None:
            hierarchy[admin_level] = []
        hierarchy[admin_level].append(relation)
    pprint.pprint(hierarchy)


def extract_admin_relation(map: Waifu) -> List[List[str]]:
    admin_relation = []
    for id in map.relation_dict:
        flag_type_boundary = False
        flag_boundary_administrative = False
        admin_level = ""
        name = ""
        ref = ""
        this_relation = map.relation_dict[id]
        for key in this_relation.tags:
            if key == "type" and this_relation.tags[key] == "boundary":
                flag_type_boundary = True
            if (
                key == "boundary"
                and this_relation.tags[key] == "administrative"
            ):
                flag_boundary_administrative = True
            if (
                flag_type_boundary == True
                and flag_boundary_administrative == True
            ):
                if "admin_level" in this_relation.tags:
                    admin_level = this_relation.tags["admin_level"]
                if "name" in this_relation.tags:
                    name = this_relation.tags["name"]
                if "ref" in this_relation.tags:
                    ref = this_relation.tags["ref"]
        admin_relation.append([id, admin_level, name, ref])
    return admin_relation


def extract_tree(admin_relation: List[List[str]], map: Waifu) -> list:
    admin_tree = []
    # 是否需要手动指定根节点？
    # 在找得到唯一的最高等级的时候可以直接用，但如果就是查非最高级开始的咋办
    # 然后就是逐个访问了，这里建议深度优先策略

    strategy_root = "auto"  # highest=指定最高级的，不行就炸，auto就是上述判断不行就要求手输，input就是手输为重
    if strategy_root == "auto" or strategy_root == "highest":
        highest_admin_value = 999
        highest_admin_id = 0
        highest_admin_count = 0
        highest_admin = []
        for relation in admin_relation:
            if highest_admin_value!="" and (int(relation[1]) <= int(highest_admin_value)):
                highest_admin_value = relation[1]
                highest_admin_id = relation[0]
                highest_admin_count += 1
                highest_admin.append([highest_admin_id, highest_admin_value])
        print(highest_admin)
        if highest_admin_count > 1:
            # 查找失败
            highest_admin_id = input("请输入要查询的根关系的id")
            print(highest_admin_id)
        else:
            print(highest_admin_id)
    elif strategy_root == "input":
        highest_admin_id = input("请输入要查询的根关系的id")
        print(highest_admin_id)
    else:
        print("¿")

    return admin_tree


def main():
    map = Waifu()
    map.read(mode="file", file_path="map.osm")
    admin_relation = extract_admin_relation(map)
    show_hierarchy(admin_relation)
    extract_tree(admin_relation,map)


if __name__ == "__main__":
    main()
