import pprint
from typing import Dict, List, Optional

from kqs.waifu import Waifu


def i18n_string(strid: str):
    if strid == "enter-root-id":
        return "请输入要查询的根关系的id:"


def show_hierarchy(relation_list: List[List[str]]) -> None:
    hierarchy: Dict[str, List[List[str]]] = {}
    for relation in relation_list:
        admin_level = relation[1]
        if hierarchy.get(admin_level) == None:
            hierarchy[admin_level] = []
        hierarchy[admin_level].append(relation)
    pprint.pprint(hierarchy)
    print("=" * 50)


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


def get_highest_admin_id(
    admin_relation: List[List[str]], extract_strategy="auto"
) -> Optional[int]:
    # auto=就是上述判断不行就要求手输
    # highest=指定最高级的，不行就炸
    # input=Manual assign directly.

    if extract_strategy == "auto" or extract_strategy == "highest":
        highest_admin_id = 0
        highest_admin_value = 999
        highest_admin_count = 0
        highest_admin = []
        for relation in admin_relation:
            if relation[1] != "":
                if int(relation[1]) <= int(highest_admin_value):
                    highest_admin_value = int(relation[1])
                    highest_admin_id = int(relation[0])
                    highest_admin_count += 1
                    highest_admin.append(
                        [highest_admin_id, highest_admin_value]
                    )
        print(highest_admin)
        if extract_strategy == "highest":
            return None
        else:
            if highest_admin_count > 1:
                # Multiple result, need manual assign.
                highest_admin_id = input(i18n_string("enter-root-id"))
    elif extract_strategy == "input":
        highest_admin_id = input(i18n_string("enter-root-id"))
    else:
        return None
    print(highest_admin_id)
    return highest_admin_id


def extract_tree(admin_relation: List[List[str]], map: Waifu) -> list:
    highest_admin_id = get_highest_admin_id(admin_relation)

    def extract_subarea(current_relation_id: int) -> list:
        tree = []
        relation = map.relation_dict[current_relation_id]
        members = [
            {"type": x.type, "ref": x.ref, "role": x.role}
            for x in relation.members
        ]
        subareas = []
        for member in members:
            if member["role"] == "subarea":

                def is_subarea_downloaded(subarea_id: int):
                    if subarea_id in map.relation_dict:
                        return True
                    else:
                        return False

                subareas.append(
                    [
                        current_relation_id,
                        member["ref"],
                        is_subarea_downloaded(member["ref"]),
                    ]
                )
        # print(subareas)
        if len(subareas) > 0:
            for subarea in subareas:
                if subarea[2] == True:
                    tree.append(subarea.append(extract_subarea(subarea[1])))
        else:
            return []

        return tree
    return extract_subarea(highest_admin_id)


def main():
    map = Waifu()
    map.read(mode="file", file_path="map.osm")
    admin_relation = extract_admin_relation(map)
    show_hierarchy(admin_relation)
    admin_tree = extract_tree(admin_relation, map)
    print(admin_tree)


if __name__ == "__main__":
    main()
