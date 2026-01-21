"""Standaard topic types configuratie voor Digital Coach provisioning.

Deze module bevat een representatieve subset van AskDelphi topic types
gebruikt voor Digital Coach homepagina's, procespagina's, stappen en instructies.

Topic Type Gebruik:
- Digitale Coach Homepagina (a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6):
  Root topic voor een Digital Coach proces. Gebruikt als top-level container.
  
- Digitale Coach Procespagina (b2c3d4e5-f6a7-48b9-c0d1-e2f3a4b5c6d7):
  Procespagina topic. Vertegenwoordigt een grote sectie of proces in de coach.
  
- Digitale Coach Stap (c3d4e5f6-a7b8-49ca-d1e2-f3a4b5c6d7e8):
  Stap topic. Vertegenwoordigt een enkele stap binnen een proces.
  
- Digitale Coach Instructie (d4e5f6a7-b8c9-4adb-e2f3-a4b5c6d7e8f9):
  Instructie topic. Vertegenwoordigt gedetailleerde instructies voor een stap.

Uitgebreide Topic Types:
- Gebruikt voor gespecialiseerde content types (Questionnaire, Video, Task, etc.)
- Kunnen gebruikt worden als alternatief of aanvulling op Digital Coach types
- Elk heeft een unieke UUID en namespace
"""

import uuid

DEFAULT_TOPIC_TYPES = [
    {
        "key": uuid.UUID("a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6"),
        "title": "Digitale Coach Homepagina",
        "displayName": "Digitale Coach Homepagina",
        "namespace": "AskDelphi.DigitalCoach",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("b2c3d4e5-f6a7-48b9-c0d1-e2f3a4b5c6d7"),
        "title": "Digitale Coach Procespagina",
        "displayName": "Digitale Coach Procespagina",
        "namespace": "AskDelphi.DigitalCoach",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("c3d4e5f6-a7b8-49ca-d1e2-f3a4b5c6d7e8"),
        "title": "Digitale Coach Stap",
        "displayName": "Digitale Coach Stap",
        "namespace": "AskDelphi.DigitalCoach",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("d4e5f6a7-b8c9-4adb-e2f3-a4b5c6d7e8f9"),
        "title": "Digitale Coach Instructie",
        "displayName": "Digitale Coach Instructie",
        "namespace": "AskDelphi.DigitalCoach",
        "isDeleted": False,
    },
    # Extended topic types (UUID keys)
    {
        "key": uuid.UUID("c1225506-63e2-4785-9e51-06a587d54a9c"),
        "title": "Questionnaire",
        "displayName": "Questionnaire",
        "namespace": "http://tempuri.org/imola-questionnaire",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("dac8be46-310c-4000-a6ae-0b598ea55ae7"),
        "title": "Image map",
        "displayName": "Image map",
        "namespace": "http://tempuri.org/doppio-imagemap",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("67466b32-3842-44bf-9f68-0cedb5efa199"),
        "title": "Profile details portlet",
        "displayName": "Profile details portlet",
        "namespace": "http://tempuri.org/imola-profile-details-portlet",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("791702ff-4dc9-443d-bba8-0f28a3639f3b"),
        "title": "Expandable items",
        "displayName": "Expandable items",
        "namespace": "http://tempuri.org/imola-expandable-content",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("d89f511e-b8c8-437c-ba9d-116d3ed6b146"),
        "title": "My profile",
        "displayName": "My profile",
        "namespace": "http://tempuri.org/imola-profile",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("d2d2da24-7d44-46e1-808a-11fe621347c3"),
        "title": "Tabbed portlet",
        "displayName": "Tabbed portlet",
        "namespace": "http://tempuri.org/imola-tabbed-portlet",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("be94f430-64b1-4000-a2a5-1a5a151426bf"),
        "title": "Skill area",
        "displayName": "Skill area",
        "namespace": "http://tempuri.org/imola-skill-area",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("e5a7b60c-5b45-45b5-8c00-2bfaa4b068b4"),
        "title": "ConnectPeople",
        "displayName": "ConnectPeople",
        "namespace": "http://tempuri.org/doppio-external",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("8959002a-806f-4c7d-a47d-2e36c66d4d6c"),
        "title": "SharePoint",
        "displayName": "SharePoint",
        "namespace": "http://tempuri.org/doppio-external",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("8f96ac4b-5bf7-448e-9d14-3308c201aa96"),
        "title": "Gallery",
        "displayName": "Gallery",
        "namespace": "http://tempuri.org/doppio-gallery",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("6c881829-a743-4522-b4a3-33dcedc2d6d5"),
        "title": "Micropolling definition",
        "displayName": "Micropolling definition",
        "namespace": "http://tempuri.org/imola-micro-polling-definition",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("aece62fc-2ed5-48c3-8508-36c28d1e02b1"),
        "title": "Blob",
        "displayName": "Blob",
        "namespace": "http://tempuri.org/doppio-blob",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("20dc729a-beb0-4d01-b020-3cd8d9383c3c"),
        "title": "Publication Reference",
        "displayName": "Publication Reference",
        "namespace": "http://tempuri.org/imola-publication-reference",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("72aaefbb-1c09-4f89-8830-54194b03523b"),
        "title": "Pre-defined search",
        "displayName": "Pre-defined search",
        "namespace": "http://tempuri.org/imola-pre-defined-search",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("ba75b3b4-d3cb-4e89-a899-62c627854cb8"),
        "title": "Uitgeverij extern",
        "displayName": "Uitgeverij extern",
        "namespace": "http://tempuri.org/doppio-external",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("38a23602-65f5-4d32-96c5-770280116f8e"),
        "title": "Homepage",
        "displayName": "Homepage",
        "namespace": "http://tempuri.org/imola-homepage",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("5d9a3a07-0ab3-4cb1-9158-78843c0f08a9"),
        "title": "Cornerstone",
        "displayName": "Cornerstone",
        "namespace": "http://tempuri.org/doppio-external",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("4f5e8ca7-b40a-42bc-beb6-7d419b94f189"),
        "title": "Flipcard Portlet",
        "displayName": "Flipcard Portlet",
        "namespace": "http://tempuri.org/imola-flipcard-portlet",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("ae4dd3b4-3d52-4144-87fd-804c614051d4"),
        "title": "Concept",
        "displayName": "Concept",
        "namespace": "http://tempuri.org/imola-concept",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("bbd6f557-2246-472f-aa2e-830745a3f462"),
        "title": "Btube Link",
        "displayName": "Btube Link",
        "namespace": "http://tempuri.org/doppio-external",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("6aba8437-c8df-42d2-a868-840847c124ca"),
        "title": "Task",
        "displayName": "Task",
        "namespace": "http://tempuri.org/imola-task",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("64707088-30a9-45f3-a4cf-8d60e43ac965"),
        "title": "External URL",
        "displayName": "External URL",
        "namespace": "http://tempuri.org/doppio-external",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("ece342d0-593a-4c22-828f-8db6934ecec3"),
        "title": "Intranet",
        "displayName": "Intranet",
        "namespace": "http://tempuri.org/doppio-external",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("776892da-9f31-4856-8f3d-9196fceb3755"),
        "title": "Hierarchy",
        "displayName": "Hierarchy",
        "namespace": "http://tempuri.org/doppio-hierarchy",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("7c9e88e5-e99a-4f04-8ebc-9c1cf7f19931"),
        "title": "Rakoo",
        "displayName": "Rakoo",
        "namespace": "http://tempuri.org/doppio-external",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("401b40ee-da71-4bdb-abf1-aede6542f0b0"),
        "title": "Moodle",
        "displayName": "Moodle",
        "namespace": "http://tempuri.org/doppio-external",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("3af3bf81-6a7e-4938-860b-afe2c97234df"),
        "title": "Person",
        "displayName": "Person",
        "namespace": "http://tempuri.org/imola-person",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("c568af9a-6c89-45cf-a580-bc94e1c62ae3"),
        "title": "Action",
        "displayName": "Action",
        "namespace": "http://tempuri.org/imola-action",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("bbce37d3-2023-4d93-80ca-bd3a6722143d"),
        "title": "Pagina Structuur Voorgedefinieerde Zoekopdracht",
        "displayName": "Pagina Structuur Voorgedefinieerde Zoekopdracht",
        "namespace": "http://tempuri.org/imola-pre-defined-search",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("ee51338e-4057-4beb-9223-bf40d1a43336"),
        "title": "Collection",
        "displayName": "Collection",
        "namespace": "http://tempuri.org/imola-collection",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("b740c526-a677-4663-8704-c1db9767f9a5"),
        "title": "Video",
        "displayName": "Video",
        "namespace": "http://tempuri.org/imola-video",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("eb25fa77-2bdc-42a2-8df0-cf1dbd06b104"),
        "title": "Quick question",
        "displayName": "Quick question",
        "namespace": "http://tempuri.org/imola-quick-question",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("22cd8efa-bd6c-4439-86fd-d1c6cb20ea21"),
        "title": "Menu",
        "displayName": "Menu",
        "namespace": "http://tempuri.org/imola-menu",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("4a50fb1c-8645-4bb7-b5c9-d74a98181d73"),
        "title": "Image",
        "displayName": "Image",
        "namespace": "http://tempuri.org/doppio-image",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("4ffc6ab8-ae5a-42f0-bc79-e37e7b70fce3"),
        "title": "Glossary item",
        "displayName": "Glossary item",
        "namespace": "http://tempuri.org/imola-glossary-item",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("e647b854-7f0c-4268-9946-f49935795bc7"),
        "title": "Simple topic",
        "displayName": "Simple topic",
        "namespace": "http://tempuri.org/imola-simple-topic",
        "isDeleted": False,
    },
    {
        "key": uuid.UUID("20d314fc-f8ca-4f89-ab39-f50fca17ceb8"),
        "title": "Sketchbook",
        "displayName": "Sketchbook",
        "namespace": "http://tempuri.org/imola-sketchbook",
        "isDeleted": False,
    },
]
