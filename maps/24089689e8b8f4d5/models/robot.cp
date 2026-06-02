{
    "deviceTypes": [
        {
            "devices": [
                {
                    "deviceParams": [
                        {
                            "arrayParam": {
                                "params": [
                                    {
                                        "doubleValue": 0.011293297034214445,
                                        "key": "x",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": 0.018334409861960665,
                                        "key": "y",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": -0.21166756417750318,
                                        "key": "yaw",
                                        "type": "double"
                                    }
                                ]
                            },
                            "key": "basic",
                            "type": "arrayParam"
                        }
                    ],
                    "isDisplay": true,
                    "isEnabled": true,
                    "name": "laser2"
                },
                {
                    "deviceParams": [
                        {
                            "arrayParam": {
                                "params": [
                                    {
                                        "doubleValue": 0.00478852853326478,
                                        "key": "x",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": 0.0015593875334872207,
                                        "key": "y",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": -0.18511074450373827,
                                        "key": "yaw",
                                        "type": "double"
                                    }
                                ]
                            },
                            "key": "basic",
                            "type": "arrayParam"
                        }
                    ],
                    "isDisplay": true,
                    "isEnabled": true,
                    "name": "laser"
                }
            ],
            "name": "laser"
        },
        {
            "devices": [
                {
                    "deviceParams": [
                        {
                            "arrayParam": {
                                "params": [
                                    {
                                        "doubleValue": -0.00027621418121115404,
                                        "key": "y",
                                        "type": "double"
                                    }
                                ]
                            },
                            "key": "basic",
                            "type": "arrayParam"
                        },
                        {
                            "comboParam": {
                                "childParams": [
                                    {
                                        "key": "walk",
                                        "params": [
                                            {
                                                "doubleValue": 9.47650452270965e-05,
                                                "key": "wheelRadius",
                                                "type": "double"
                                            }
                                        ]
                                    }
                                ]
                            },
                            "key": "func",
                            "type": "comboParam"
                        }
                    ],
                    "isDisplay": true,
                    "isEnabled": true,
                    "name": "left"
                },
                {
                    "deviceParams": [
                        {
                            "arrayParam": {
                                "params": [
                                    {
                                        "doubleValue": 0.00027621418121115404,
                                        "key": "y",
                                        "type": "double"
                                    }
                                ]
                            },
                            "key": "basic",
                            "type": "arrayParam"
                        },
                        {
                            "comboParam": {
                                "childParams": [
                                    {
                                        "key": "walk",
                                        "params": [
                                            {
                                                "doubleValue": -5.93600475869982e-05,
                                                "key": "wheelRadius",
                                                "type": "double"
                                            }
                                        ]
                                    }
                                ]
                            },
                            "key": "func",
                            "type": "comboParam"
                        }
                    ],
                    "isDisplay": true,
                    "isEnabled": true,
                    "name": "right"
                }
            ],
            "name": "motor"
        },
        {
            "devices": [
                {
                    "deviceParams": [
                        {
                            "arrayParam": {
                                "params": [
                                    {
                                        "doubleValue": -0.04200487163744382,
                                        "key": "x",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": 0.030965434707300454,
                                        "key": "y",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": 0.7327529359687106,
                                        "key": "qw",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": 0.0046710282786142105,
                                        "key": "qx",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": 0.0017838730051970924,
                                        "key": "qy",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": 0.6804764023249861,
                                        "key": "qz",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": -0.1492854696016577,
                                        "key": "Bax",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": -0.017570696485416287,
                                        "key": "Bay",
                                        "type": "double"
                                    },
                                    {
                                        "doubleValue": 0.011491124893080528,
                                        "key": "Baz",
                                        "type": "double"
                                    }
                                ]
                            },
                            "key": "basic",
                            "type": "arrayParam"
                        }
                    ],
                    "isDisplay": true,
                    "isEnabled": true,
                    "name": "controller"
                }
            ],
            "name": "controller"
        }
    ]
}
