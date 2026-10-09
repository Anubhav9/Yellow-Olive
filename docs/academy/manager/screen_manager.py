import pyxel

##Map is in format of current screen name as key and next screen name as value
def screen_management_map():
    manager_map={
        "screen_1_pods_introduction":"screen_2_containers",
        "screen_2_containers":"screen_3_shared_network",
        "screen_3_shared_network":"screen_4_volumes",
        "screen_4_volumes":"screen_5_pods_phases",
        "screen_5_pods_phases":"screen_6_labels",
        "screen_6_labels":"screen_7_restart_policy",
        "screen_7_restart_policy":"home_screen",
    }
    return manager_map

INTERACTIVE_PAGES = ("village_screen", "academy_hall_screen")

def screen_to_class_mapping_map(page_name):
    if(page_name=="village_screen"):
        from screens.intro.village_screen import VillageScreen
        return VillageScreen
    elif(page_name=="academy_hall_screen"):
        from screens.intro.academy_hall_screen import AcademyHallScreen
        return AcademyHallScreen
    elif(page_name=="home_screen"):
        from screens.home_screen.home_screen import HomeScreen
        return HomeScreen
    elif(page_name=="lessons_screen"):
        from screens.home_screen.lessons_screen import LessonsScreen
        return LessonsScreen
    elif(page_name=="screen_1_pods_introduction"):
        from screens.pods.screen_1_pods_introduction import PodIntroductionScreen
        return PodIntroductionScreen
    elif(page_name=="screen_2_containers"):
        from screens.pods.screen_2_containers import ContainersScreen
        return ContainersScreen
    elif(page_name=="screen_3_shared_network"):
        from screens.pods.screen_3_shared_network import SharedNetworkScreen
        return SharedNetworkScreen
    elif(page_name=="screen_4_volumes"):
        from screens.pods.screen_4_volumes import VolumesScreen
        return VolumesScreen
    elif(page_name=="screen_5_pods_phases"):
        from screens.pods.screen_5_pod_phases import PodPhasesScreen
        return PodPhasesScreen
    elif(page_name=="screen_6_labels"):
        from screens.pods.screen_6_labels import LabelsScreen
        return LabelsScreen
    elif(page_name=="screen_7_restart_policy"):
        from screens.pods.screen_7_restart_policy import RestartPolicyScreen
        return RestartPolicyScreen
