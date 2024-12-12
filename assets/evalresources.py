# evalresources.py

design_resources = {
    "dick_and_carey": [
        "https://worldofwork.io/2019/08/dick-carey-instructional-design-model/",
        "https://psu.pb.unizin.org/idhandbook/chapter/dick-carey/",
        "https://www.studentexperience.co.za/blogs/post/mastering-the-art-of-instructional-design-the-dick-and-carey-model-demystified",
    ],
    "sam": [
        "https://elmlearning.com/hub/instructional-design/sam-successive-approximation-model/",
        "https://www.howtoo.co/posts/the-complete-guide-to-the-successive-approximation-model-sam-of-instructional-design#:~:text=The%20Successive%20Approximation%20Model%20(SAM)%20is%20an%20agile%2C%20iterative,rounds%20of%20design%20and%20development.",
        "https://www.alleninteractions.com/allen-interactions-rapid-instructional-design-and-development-with-sam",
    ],
    "shackleton": [
        "https://www.linkedin.com/pulse/5di-learning-design-process-liz-ryan/",
        "https://360learning.com/blog/l-and-d-podcast-nick-shackleton-jones-learning-maturity/",
    ],
    "arches_and_spaces": [
        "https://medium.com/@eikris/designing-for-learning-introducing-the-learning-arches-affea795cf4d",
        "https://medium.com/@simonkavanagh/learning-arches-for-online-learning-b322cae49d6c",
        "https://www.kaospilot.dk/wp-content/uploads/2021/11/Kaospilot_brochure_DesignLearningSpaces_Kaospilot_webversion.pdf",
    ],
}

# TRANSFER
transfer_resources = {
    "action_mapping": [
        "https://blog.cathy-moore.com/action-mapping-a-visual-approach-to-training-design/#gref"
    ],
    "decisive_dozen": [
        "https://johndabell.com/2018/06/14/the-decisive-dozen/",
        "https://www.worklearning.com/wp-content/uploads/2018/02/Thalheimer-The-Learning-Transfer-Evaluation-Model-Version-12.pdf",
    ],
    "wiggins": [
        "https://psu.pb.unizin.org/idhandbook/chapter/wiggins-mctighe/",
    ],
}

# Performance
performance_resources = {
    "mager_and_Pipe": [
        "https://sites.google.com/view/htp7150-t3/models/mager-and-pipe-model",
        "https://hptmanualaaly.weebly.com/mager-and-pipes-model.html",
    ],
    "addie": ["https://research.com/education/the-addie-model#applications"],
    "behavior_engineering": [
        "https://instructionaldesignfusions.wordpress.com/tag/behavioral-engineering-model/"
    ],
}

design_names = [
    "Dick and Carey Instructional Design Model",
    "SAM (Successive Approximation Model)",
    "Shackleton 5Di Model",
    "Learning Arches and Learning Spaces (Kaospilot)",
]

transfer_names = [
    "Action Mapping (Cathy Moore)",
    "Learning Transfer Evaluation: The Decisive Dozen (Dr. Will Thalheimer, PhD)",
    "Wiggins and McTighe Backwards Design Model (UbD)",
]

performance_names = [
    "Mager and Pipe Model",
    "Behavior Engineering Model",
    "ADDIE Model",
]


name_map = dict(zip(list(design_resources.keys()), design_names))
name_map.update(dict(zip(list(transfer_resources.keys()), transfer_names)))
name_map.update(dict(zip(list(performance_resources.keys()), performance_names)))
