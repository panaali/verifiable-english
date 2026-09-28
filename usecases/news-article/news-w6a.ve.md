---
{
 "format": "ve-document@1",
 "environment": {
  "language": "ve.core@0.2",
  "profiles": [
   "documents@1",
   "order@0",
   "relational-fol@0",
   "time@0"
  ],
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "vocabulary": {
   "sorts": {},
   "predicates": {},
   "constants": {
    "decision_date": {
     "sort": "$int",
     "unit": "day",
     "description": "date of the reported Fed decision",
     "verbalisation": "the decision date"
    },
    "new_target_lower": {
     "sort": "$int",
     "unit": "bp",
     "description": "lower endpoint of the new target rate range in S2",
     "verbalisation": "the new target lower bound"
    },
    "new_target_upper": {
     "sort": "$int",
     "unit": "bp",
     "description": "upper endpoint of the new target rate range in S2",
     "verbalisation": "the new target upper bound"
    },
    "projected_range_lower": {
     "sort": "$int",
     "unit": "bp",
     "description": "lower endpoint of the policy-rate range projected in S6",
     "verbalisation": "the projected range lower bound"
    },
    "projected_range_upper": {
     "sort": "$int",
     "unit": "bp",
     "description": "upper endpoint of the policy-rate range projected in S6",
     "verbalisation": "the projected range upper bound"
    },
    "projected_reach_year": {
     "sort": "$int",
     "unit": "calendar_year",
     "description": "year by whose end S6 projects the range to be reached",
     "verbalisation": "the projected reaching year"
    },
    "projected_remain_year": {
     "sort": "$int",
     "unit": "calendar_year",
     "description": "year through whose end S6 projects the range to remain",
     "verbalisation": "the projected final year of the range"
    },
    "statement_goal": {
     "sort": "$int",
     "unit": "bp",
     "description": "the Committee's inflation goal named in the S7 policy statement quote",
     "verbalisation": "the Committee's stated inflation goal"
    },
    "pledged_goal": {
     "sort": "$int",
     "unit": "bp",
     "description": "the inflation level Warsh pledges in S14 to bring inflation back to",
     "verbalisation": "the pledged inflation level"
    },
    "pce_september_estimate": {
     "sort": "$int",
     "unit": "bp",
     "description": "September estimate of PCE inflation reported in S11",
     "verbalisation": "the September PCE estimate"
    },
    "pce_june_estimate": {
     "sort": "$int",
     "unit": "bp",
     "description": "June estimate of PCE inflation reported in S11",
     "verbalisation": "the June PCE estimate"
    },
    "target_rate": {
     "sort": "$int",
     "unit": "bp",
     "description": "inflation target named in S12",
     "verbalisation": "the inflation target"
    },
    "first_projected_target_year": {
     "sort": "$int",
     "unit": "calendar_year",
     "description": "first year in the selected forecast reading of S12",
     "verbalisation": "the first projected target year"
    },
    "growth_old_projection": {
     "sort": "$int",
     "unit": "bp",
     "description": "earlier projected growth figure in S13",
     "verbalisation": "the earlier growth projection"
    },
    "growth_new_projection": {
     "sort": "$int",
     "unit": "bp",
     "description": "revised projected growth figure in S13",
     "verbalisation": "the revised growth projection"
    },
    "unemployment_old_projection": {
     "sort": "$int",
     "unit": "bp",
     "description": "earlier projected unemployment figure in S13",
     "verbalisation": "the earlier unemployment projection"
    },
    "unemployment_new_projection": {
     "sort": "$int",
     "unit": "bp",
     "description": "revised projected unemployment figure in S13",
     "verbalisation": "the revised unemployment projection"
    }
   }
  },
  "unit_schema": "ve-units@1",
  "units": {
   "bp": {
    "scale": "100",
    "display": {
     "kind": "percent"
    }
   },
   "calendar_year": {
    "scale": "1",
    "display": {
     "kind": "decimal",
     "label": "calendar year",
     "placement": "prefix"
    }
   },
   "day": {
    "scale": "1",
    "display": {
     "kind": "iso_date"
    }
   }
  }
 },
 "units": [
  {
   "id": "preamble",
   "span": [
    0,
    2159
   ],
   "kind": "meta",
   "meaning": {
    "unformalised": "provenance_metadata"
   },
   "support": "none"
  },
  {
   "id": "s1_date",
   "span": [
    2159,
    2237
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "date_on",
      [
       "const",
       "day",
       "decision_date"
      ],
      [
       "date",
       "2026-09-16"
      ]
     ]
    }
   },
   "meaning_id": "e4feb48b7b054230d7d0ea03a34d2d0271572b9a623d03c323f26e4ddbb48cf3"
  },
  {
   "id": "s1_rest",
   "span": [
    2237,
    2502
   ],
   "kind": "exposition",
   "meaning": {
    "unformalised": "relational_route_claims_ve"
   },
   "support": "none"
  },
  {
   "id": "s2_causes",
   "span": [
    2502,
    2762
   ],
   "kind": "exposition",
   "meaning": {
    "unformalised": "relational_route_claims_ve"
   },
   "support": "none"
  },
  {
   "id": "s2_move",
   "span": [
    2762,
    2812
   ],
   "kind": [
    "unformalised",
    "missing_old_range"
   ],
   "meaning": {
    "unformalised": "missing_old_range"
   },
   "support": "testimony"
  },
  {
   "id": "s2_range",
   "span": [
    2812,
    2852
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "new_target_lower"
       ],
       [
        "decimal",
        "bp",
        "3.75"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "new_target_upper"
       ],
       [
        "decimal",
        "bp",
        "4.00"
       ]
      ]
     ]
    }
   },
   "meaning_id": "b7a62d01c6a28b490867e54e2bbf8aa5e91bd74862f41cec2e833febce9c8267"
  },
  {
   "id": "s3_count",
   "span": [
    2852,
    3046
   ],
   "kind": [
    "unformalised",
    "count_exceeds_bound"
   ],
   "meaning": {
    "unformalised": "count_exceeds_bound"
   },
   "support": "testimony"
  },
  {
   "id": "s4_s5",
   "span": [
    3046,
    3281
   ],
   "kind": "exposition",
   "meaning": {
    "unformalised": "relational_route_claims_ve"
   },
   "support": "none"
  },
  {
   "id": "s6_framing",
   "span": [
    3281,
    3449
   ],
   "kind": "exposition",
   "meaning": {
    "unformalised": "figurative_or_vague"
   },
   "support": "none"
  },
  {
   "id": "s6_range",
   "span": [
    3449,
    3466
   ],
   "kind": [
    "attributed",
    "fomc",
    "expects",
    "asserted"
   ],
   "meaning": "specified",
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "projected_range_lower"
       ],
       [
        "decimal",
        "bp",
        "4.00"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "projected_range_upper"
       ],
       [
        "decimal",
        "bp",
        "4.25"
       ]
      ]
     ]
    }
   },
   "meaning_id": "3bd2ba5ef5900e070561f7f137cbddef84f0ff6474013c073e21e72d69c5abb4"
  },
  {
   "id": "s6_years",
   "span": [
    3466,
    3531
   ],
   "kind": [
    "attributed",
    "fomc",
    "expects",
    "asserted"
   ],
   "meaning": {
    "open": [
     "projection_horizon"
    ]
   },
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "calendar_year",
        "projected_reach_year"
       ],
       [
        "decimal",
        "calendar_year",
        "2026"
       ]
      ],
      [
       "eq",
       [
        "const",
        "calendar_year",
        "projected_remain_year"
       ],
       [
        "decimal",
        "calendar_year",
        "2027"
       ]
      ]
     ]
    }
   },
   "meaning_id": "699d9781237b74e3ec6ab3537a878254bf28d02ca8154792466929d360f6324f"
  },
  {
   "id": "s7_quote",
   "span": [
    3531,
    3658
   ],
   "kind": "exposition",
   "meaning": {
    "unformalised": "vague_timelier"
   },
   "support": "none"
  },
  {
   "id": "s7_goal",
   "span": [
    3658,
    3667
   ],
   "kind": [
    "attributed",
    "fomc",
    "says",
    "asserted"
   ],
   "meaning": "specified",
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "const",
       "bp",
       "statement_goal"
      ],
      [
       "decimal",
       "bp",
       "2"
      ]
     ]
    }
   },
   "meaning_id": "3c124a26bc5620de1e59319f308331ab69e4cb70d90f34ece19843552cbc5430"
  },
  {
   "id": "s7_rest",
   "span": [
    3667,
    3700
   ],
   "kind": "exposition",
   "meaning": {
    "unformalised": "relational_route_claims_ve"
   },
   "support": "none"
  },
  {
   "id": "s8_s10",
   "span": [
    3700,
    4286
   ],
   "kind": "exposition",
   "meaning": {
    "unformalised": "relational_route_claims_ve"
   },
   "support": "none"
  },
  {
   "id": "s11_pce",
   "span": [
    4286,
    4425
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "pce_september_estimate"
       ],
       [
        "decimal",
        "bp",
        "3.7"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "pce_june_estimate"
       ],
       [
        "decimal",
        "bp",
        "3.6"
       ]
      ]
     ]
    }
   },
   "meaning_id": "99ab87c4293b7c88beda3ec3d96c486831173a2dc8aa84ba233fe012dc0c02ec"
  },
  {
   "id": "s12_target",
   "span": [
    4425,
    4488
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "const",
       "bp",
       "target_rate"
      ],
      [
       "decimal",
       "bp",
       "2"
      ]
     ]
    }
   },
   "meaning_id": "918429df38b22b20be5ddb8aa6ecfc7e6661cff23ca0ea79ad5a254138cc2a9c"
  },
  {
   "id": "s12_year",
   "span": [
    4488,
    4499
   ],
   "kind": [
    "attributed",
    "fomc",
    "expects",
    "asserted"
   ],
   "meaning": "specified",
   "support": "testimony"
  },
  {
   "id": "s12_later",
   "span": [
    4499,
    4543
   ],
   "kind": [
    "unformalised",
    "missing_previous_expectation"
   ],
   "meaning": {
    "unformalised": "missing_previous_expectation"
   },
   "support": "testimony"
  },
  {
   "id": "s13_slightly",
   "span": [
    4543,
    4594
   ],
   "kind": "exposition",
   "meaning": {
    "unformalised": "vague_degree"
   },
   "support": "none"
  },
  {
   "id": "s13_growth",
   "span": [
    4594,
    4612
   ],
   "kind": [
    "attributed",
    "fomc",
    "expects",
    "asserted"
   ],
   "meaning": "specified",
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "growth_old_projection"
       ],
       [
        "decimal",
        "bp",
        "2.2"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "growth_new_projection"
       ],
       [
        "decimal",
        "bp",
        "2.3"
       ]
      ]
     ]
    }
   },
   "meaning_id": "18b3ba2a9d78b08eeb935e5975da62ea252470198ef307fc535133e89ce5ac4a"
  },
  {
   "id": "s13_unemployment",
   "span": [
    4612,
    4686
   ],
   "kind": [
    "attributed",
    "fomc",
    "expects",
    "asserted"
   ],
   "meaning": "specified",
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "unemployment_old_projection"
       ],
       [
        "decimal",
        "bp",
        "4.3"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "unemployment_new_projection"
       ],
       [
        "decimal",
        "bp",
        "4.1"
       ]
      ]
     ]
    }
   },
   "meaning_id": "87adbd2f65f1e24dafe94aaa912447cc79d36021b471268b7be69ca55d7a0816"
  },
  {
   "id": "s14_goal",
   "span": [
    4686,
    4755
   ],
   "kind": [
    "attributed",
    "warsh",
    "promised",
    "asserted"
   ],
   "meaning": "specified",
   "support": "testimony",
   "content": {
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "const",
       "bp",
       "pledged_goal"
      ],
      [
       "decimal",
       "bp",
       "2"
      ]
     ]
    }
   },
   "meaning_id": "9d84c23f5ac13cf17df6fad4739d50d5c4cf8983f00f783a8fa16041db55bbcb"
  },
  {
   "id": "s14_rest",
   "span": [
    4755,
    4818
   ],
   "kind": "exposition",
   "meaning": {
    "unformalised": "vague_pledge_manner"
   },
   "support": "none"
  },
  {
   "id": "quotation",
   "span": [
    4818,
    5448
   ],
   "kind": "meta",
   "meaning": {
    "unformalised": "duplicate_of_paraphrase"
   },
   "support": "none"
  }
 ],
 "open_terms": [
  {
   "name": "projection_horizon",
   "arguments": [],
   "decided_by": "reader",
   "necessary": [],
   "sufficient": [],
   "factors": [
    "'by the end of 2026' and 'remain there through the end of 2027' are temporal obligations of a projection, not observed future rates"
   ],
   "precedents": [],
   "jurisdiction": "news_reading",
   "version": 1
  }
 ],
 "reading_sets": [
  {
   "id": "first_target_year",
   "unit": "s12_year",
   "version": 1,
   "status": "open",
   "readings": [
    {
     "id": "equal",
     "kind": "asserted",
     "meaning_id": "696670f6e972785c3903b22452fd6a0e99acfc2835f0c0c7aa770c7d56710a05",
     "content": {
      "format": "ve-quantity@1",
      "formula": [
       "eq",
       [
        "const",
        "calendar_year",
        "first_projected_target_year"
       ],
       [
        "decimal",
        "calendar_year",
        "2029"
       ]
      ]
     },
     "admission": {
      "who": "w6a_builder",
      "why": "'not projected to reach ... until 2029' as the first year ",
      "distinguishing_models": {
       "lower_bound": "2aa3245ec24724778d2e9315cb7605a1f0d7af6d186ed92f1867985927204354"
      }
     }
    },
    {
     "id": "lower_bound",
     "kind": "asserted",
     "meaning_id": "285d116cd43b9ecac7973805beb0f117fabbf937ca66cbabf9180392c042bd8f",
     "content": {
      "format": "ve-quantity@1",
      "formula": [
       "le",
       [
        "decimal",
        "calendar_year",
        "2029"
       ],
       [
        "const",
        "calendar_year",
        "first_projected_target_year"
       ]
      ]
     },
     "admission": {
      "who": "w6a_builder",
      "why": "'not ... until 2029' read only as a lower bound ",
      "distinguishing_models": {
       "equal": "2aa3245ec24724778d2e9315cb7605a1f0d7af6d186ed92f1867985927204354"
      }
     }
    }
   ],
   "models": {
    "2aa3245ec24724778d2e9315cb7605a1f0d7af6d186ed92f1867985927204354": {
     "complete": true,
     "domains": {},
     "constants": {
      "decision_date": "20712",
      "first_projected_target_year": "2030",
      "growth_new_projection": "230",
      "growth_old_projection": "220",
      "new_target_lower": "375",
      "new_target_upper": "400",
      "pce_june_estimate": "360",
      "pce_september_estimate": "370",
      "pledged_goal": "200",
      "projected_range_lower": "400",
      "projected_range_upper": "425",
      "projected_reach_year": "2026",
      "projected_remain_year": "2027",
      "statement_goal": "200",
      "target_rate": "200",
      "unemployment_new_projection": "410",
      "unemployment_old_projection": "430"
     },
     "relations": {}
    }
   }
  }
 ],
 "graph": {
  "root": "news_consequences",
  "nodes": [
   {
    "name": "n01",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "date_on",
      [
       "const",
       "day",
       "decision_date"
      ],
      [
       "date",
       "2026-09-16"
      ]
     ]
    },
    "unit": "s1_date"
   },
   {
    "name": "n07",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "new_target_lower"
       ],
       [
        "decimal",
        "bp",
        "3.75"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "new_target_upper"
       ],
       [
        "decimal",
        "bp",
        "4.00"
       ]
      ]
     ]
    },
    "unit": "s2_range"
   },
   {
    "name": "n13",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "projected_range_lower"
       ],
       [
        "decimal",
        "bp",
        "4.00"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "projected_range_upper"
       ],
       [
        "decimal",
        "bp",
        "4.25"
       ]
      ]
     ]
    },
    "label": "bridge:accepts(fomc,s6_range)"
   },
   {
    "name": "n13y",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "calendar_year",
        "projected_reach_year"
       ],
       [
        "decimal",
        "calendar_year",
        "2026"
       ]
      ],
      [
       "eq",
       [
        "const",
        "calendar_year",
        "projected_remain_year"
       ],
       [
        "decimal",
        "calendar_year",
        "2027"
       ]
      ]
     ]
    },
    "label": "bridge:accepts(fomc,s6_years)"
   },
   {
    "name": "n15",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "const",
       "bp",
       "statement_goal"
      ],
      [
       "decimal",
       "bp",
       "2"
      ]
     ]
    },
    "label": "bridge:accepts(fomc,s7_goal)"
   },
   {
    "name": "n21",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "pce_september_estimate"
       ],
       [
        "decimal",
        "bp",
        "3.7"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "pce_june_estimate"
       ],
       [
        "decimal",
        "bp",
        "3.6"
       ]
      ]
     ]
    },
    "unit": "s11_pce"
   },
   {
    "name": "n22",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "const",
       "bp",
       "target_rate"
      ],
      [
       "decimal",
       "bp",
       "2"
      ]
     ]
    },
    "unit": "s12_target"
   },
   {
    "name": "n22y",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "or",
      [
       "eq",
       [
        "const",
        "calendar_year",
        "first_projected_target_year"
       ],
       [
        "decimal",
        "calendar_year",
        "2029"
       ]
      ],
      [
       "le",
       [
        "decimal",
        "calendar_year",
        "2029"
       ],
       [
        "const",
        "calendar_year",
        "first_projected_target_year"
       ]
      ]
     ]
    },
    "label": "readings:first_target_year@1:all"
   },
   {
    "name": "n23g",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "growth_old_projection"
       ],
       [
        "decimal",
        "bp",
        "2.2"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "growth_new_projection"
       ],
       [
        "decimal",
        "bp",
        "2.3"
       ]
      ]
     ]
    },
    "label": "bridge:accepts(fomc,s13_growth)"
   },
   {
    "name": "n23u",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "eq",
       [
        "const",
        "bp",
        "unemployment_old_projection"
       ],
       [
        "decimal",
        "bp",
        "4.3"
       ]
      ],
      [
       "eq",
       [
        "const",
        "bp",
        "unemployment_new_projection"
       ],
       [
        "decimal",
        "bp",
        "4.1"
       ]
      ]
     ]
    },
    "label": "bridge:accepts(fomc,s13_unemployment)"
   },
   {
    "name": "n24",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "const",
       "bp",
       "pledged_goal"
      ],
      [
       "decimal",
       "bp",
       "2"
      ]
     ]
    },
    "label": "bridge:accepts(warsh,s14_goal)"
   },
   {
    "name": "N07-order",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "lt",
      [
       "const",
       "bp",
       "new_target_lower"
      ],
      [
       "const",
       "bp",
       "new_target_upper"
      ]
     ]
    },
    "premises": [
     "n07"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "b7a62d01c6a28b490867e54e2bbf8aa5e91bd74862f41cec2e833febce9c8267"
     ],
     "conclusion_meaning_id": "24c7b2345f47d515d56e99e90438a356e2b308b8aed1cf700bdf31296b424b5d",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "cdea5db3a3f09bd3b4f27d9eb97bb14d846daf57da3baec5159a720f2a7d4e7d"
      ],
      "conclusion_meaning_id": "c2e6a14cb1987671a0aeaacd15673212fa0eabfdc0cb7ecd6c296e7dcb98a793",
      "trace": {
       "rule": "expand",
       "at": 0,
       "children": [
        {
         "rule": "order-farkas@1",
         "cuts": [],
         "literals": [
          [
           1,
           "1"
          ],
          [
           2,
           "1"
          ],
          [
           3,
           "-1"
          ]
         ],
         "final_cuts": []
        }
       ]
      }
     }
    }
   },
   {
    "name": "N13-order",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "lt",
      [
       "const",
       "bp",
       "projected_range_lower"
      ],
      [
       "const",
       "bp",
       "projected_range_upper"
      ]
     ]
    },
    "premises": [
     "n13"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "3bd2ba5ef5900e070561f7f137cbddef84f0ff6474013c073e21e72d69c5abb4"
     ],
     "conclusion_meaning_id": "9bd045422445381552b595ee5f5a2f44cf45608fd07eb22fab30c8d5014b6fb1",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "1cefdfdada4673166324d3ae35b359b3a7d4ae4a287cc95dd5cf2409a5db1e41"
      ],
      "conclusion_meaning_id": "44cd2de4d050a6f544c0b1479b4a75d732f6b5c4d08b8622d534e5cf84600204",
      "trace": {
       "rule": "expand",
       "at": 0,
       "children": [
        {
         "rule": "order-farkas@1",
         "cuts": [],
         "literals": [
          [
           1,
           "1"
          ],
          [
           2,
           "1"
          ],
          [
           3,
           "-1"
          ]
         ],
         "final_cuts": []
        }
       ]
      }
     }
    }
   },
   {
    "name": "N13-years",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "lt",
      [
       "const",
       "calendar_year",
       "projected_reach_year"
      ],
      [
       "const",
       "calendar_year",
       "projected_remain_year"
      ]
     ]
    },
    "premises": [
     "n13y"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "699d9781237b74e3ec6ab3537a878254bf28d02ca8154792466929d360f6324f"
     ],
     "conclusion_meaning_id": "7c60e976a1d0cdda401526a9f3c7209e0094d62167585b4ee0ab4f0a52925579",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "50e41ad55d38901334b24c23e1784742e931a357b959b7a7d7a688bf2e89a1d3"
      ],
      "conclusion_meaning_id": "c187dc3d0ab020baca0c407475831169f67d786142a8470eef25c64d1faf74e3",
      "trace": {
       "rule": "expand",
       "at": 0,
       "children": [
        {
         "rule": "order-farkas@1",
         "cuts": [],
         "literals": [
          [
           1,
           "1"
          ],
          [
           2,
           "1"
          ],
          [
           3,
           "-1"
          ]
         ],
         "final_cuts": []
        }
       ]
      }
     }
    }
   },
   {
    "name": "N15-N24-same-goal",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "const",
       "bp",
       "statement_goal"
      ],
      [
       "const",
       "bp",
       "pledged_goal"
      ]
     ]
    },
    "premises": [
     "n15",
     "n24"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "3c124a26bc5620de1e59319f308331ab69e4cb70d90f34ece19843552cbc5430",
      "9d84c23f5ac13cf17df6fad4739d50d5c4cf8983f00f783a8fa16041db55bbcb"
     ],
     "conclusion_meaning_id": "57697ca9e5e718ee9d1ff85a8298e4dceadf4b690184af0ced92589bb8ce7a1d",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "131e70c0aa6ae4e831b2010a70cb0f44563b965102c63ffc06b34247f74bc26a",
       "68c142adba1a8d9e3ad272270e897de00d7e88859f1ed8b7432a2bbb28bec740"
      ],
      "conclusion_meaning_id": "2447696f72adb5fe7d39db02e71beffc64bc5f7ee6b396db22d103eb794c54e5",
      "trace": {
       "rule": "order-neq@1",
       "at": 2,
       "children": [
        {
         "rule": "order-farkas@1",
         "cuts": [],
         "literals": [
          [
           0,
           "-1"
          ],
          [
           1,
           "1"
          ],
          [
           3,
           "1"
          ]
         ],
         "final_cuts": []
        },
        {
         "rule": "order-farkas@1",
         "cuts": [],
         "literals": [
          [
           0,
           "1"
          ],
          [
           1,
           "-1"
          ],
          [
           3,
           "1"
          ]
         ],
         "final_cuts": []
        }
       ]
      }
     }
    }
   },
   {
    "name": "N21-order",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "lt",
      [
       "const",
       "bp",
       "pce_june_estimate"
      ],
      [
       "const",
       "bp",
       "pce_september_estimate"
      ]
     ]
    },
    "premises": [
     "n21"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "99ab87c4293b7c88beda3ec3d96c486831173a2dc8aa84ba233fe012dc0c02ec"
     ],
     "conclusion_meaning_id": "338aaac563e2da2148a74c801957720d5b717ddbe1cf11270ca9b299ea0abdb1",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "3357f8eccfcd1cff8f3053db69a94d59cf78925f9b86ad7d5b9ccb640b79e6c6"
      ],
      "conclusion_meaning_id": "904c5a842f5a0785dee5709211674bd657b9108ae189ab3c3e9f04b7fe734833",
      "trace": {
       "rule": "expand",
       "at": 0,
       "children": [
        {
         "rule": "order-farkas@1",
         "cuts": [],
         "literals": [
          [
           1,
           "1"
          ],
          [
           2,
           "-1"
          ],
          [
           3,
           "1"
          ]
         ],
         "final_cuts": []
        }
       ]
      }
     }
    }
   },
   {
    "name": "N21-difference",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "add",
       "bp",
       [
        "const",
        "bp",
        "pce_september_estimate"
       ],
       [
        "scale",
        "bp",
        "-1",
        [
         "const",
         "bp",
         "pce_june_estimate"
        ]
       ]
      ],
      [
       "num",
       "bp",
       "10"
      ]
     ]
    },
    "premises": [
     "n21"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "99ab87c4293b7c88beda3ec3d96c486831173a2dc8aa84ba233fe012dc0c02ec"
     ],
     "conclusion_meaning_id": "eff7e11e1d3cb1fc3a4beeb41f56b59cb6bda7bc60421935fb1620c51a52c2ba",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "3357f8eccfcd1cff8f3053db69a94d59cf78925f9b86ad7d5b9ccb640b79e6c6"
      ],
      "conclusion_meaning_id": "5a4c72f50a2b77ebfddc58e58295b27c2bc13756384b46c0255a74347cf95af1",
      "trace": {
       "rule": "expand",
       "at": 0,
       "children": [
        {
         "rule": "order-neq@1",
         "at": 1,
         "children": [
          {
           "rule": "order-farkas@1",
           "cuts": [],
           "literals": [
            [
             2,
             "-1"
            ],
            [
             3,
             "1"
            ],
            [
             4,
             "1"
            ]
           ],
           "final_cuts": []
          },
          {
           "rule": "order-farkas@1",
           "cuts": [],
           "literals": [
            [
             2,
             "1"
            ],
            [
             3,
             "-1"
            ],
            [
             4,
             "1"
            ]
           ],
           "final_cuts": []
          }
         ]
        }
       ]
      }
     }
    }
   },
   {
    "name": "N22-year-lower-bound",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "le",
      [
       "decimal",
       "calendar_year",
       "2029"
      ],
      [
       "const",
       "calendar_year",
       "first_projected_target_year"
      ]
     ]
    },
    "premises": [
     "n22y"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "3a4f9455f12daa0aed458351116a87172f9754a0b72c454c439b7dc335490237"
     ],
     "conclusion_meaning_id": "285d116cd43b9ecac7973805beb0f117fabbf937ca66cbabf9180392c042bd8f",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "47de3fda1fb982303d0d929b7d0f32505ae6c0bd819b26e177942fd280fd2673"
      ],
      "conclusion_meaning_id": "447b0a0a859bfd7a58f81f49134ed7cc0cbc0a127bfb517bb313f0aa0e4da110",
      "trace": {
       "rule": "expand",
       "at": 0,
       "children": [
        {
         "rule": "order-farkas@1",
         "cuts": [],
         "literals": [
          [
           1,
           "1"
          ],
          [
           2,
           "-1"
          ]
         ],
         "final_cuts": []
        },
        {
         "rule": "close"
        }
       ]
      }
     }
    }
   },
   {
    "name": "N23-growth-increase",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "add",
       "bp",
       [
        "const",
        "bp",
        "growth_new_projection"
       ],
       [
        "scale",
        "bp",
        "-1",
        [
         "const",
         "bp",
         "growth_old_projection"
        ]
       ]
      ],
      [
       "num",
       "bp",
       "10"
      ]
     ]
    },
    "premises": [
     "n23g"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "18b3ba2a9d78b08eeb935e5975da62ea252470198ef307fc535133e89ce5ac4a"
     ],
     "conclusion_meaning_id": "bf3bd2518f4bd6775588027fc15913876e5953fa06dee8752b3415bba7d11e66",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "692332cc16801dfc61418fbea01a4afec439c04bebe49db8c7a0b73149fd4545"
      ],
      "conclusion_meaning_id": "d3aaa0f62857fe811055bc45067badfbce3e3b71731ca0f27e67d4a443ff7445",
      "trace": {
       "rule": "expand",
       "at": 0,
       "children": [
        {
         "rule": "order-neq@1",
         "at": 1,
         "children": [
          {
           "rule": "order-farkas@1",
           "cuts": [],
           "literals": [
            [
             2,
             "1"
            ],
            [
             3,
             "-1"
            ],
            [
             4,
             "1"
            ]
           ],
           "final_cuts": []
          },
          {
           "rule": "order-farkas@1",
           "cuts": [],
           "literals": [
            [
             2,
             "-1"
            ],
            [
             3,
             "1"
            ],
            [
             4,
             "1"
            ]
           ],
           "final_cuts": []
          }
         ]
        }
       ]
      }
     }
    }
   },
   {
    "name": "N23-unemployment-decrease",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "eq",
      [
       "add",
       "bp",
       [
        "const",
        "bp",
        "unemployment_old_projection"
       ],
       [
        "scale",
        "bp",
        "-1",
        [
         "const",
         "bp",
         "unemployment_new_projection"
        ]
       ]
      ],
      [
       "num",
       "bp",
       "20"
      ]
     ]
    },
    "premises": [
     "n23u"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "87adbd2f65f1e24dafe94aaa912447cc79d36021b471268b7be69ca55d7a0816"
     ],
     "conclusion_meaning_id": "0a2240fa7700e4885388a3467a11e5046dccc54e1e364602a152e714538cfde5",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "87d33be09bcbdedff27ca8af197a9bca1ee4b2ea280917caa75a6cad69982119"
      ],
      "conclusion_meaning_id": "f3fe3f431cb95e0c1d8969eba47c5dd413b3e19c0ff779d9efa4154f77fc244b",
      "trace": {
       "rule": "expand",
       "at": 0,
       "children": [
        {
         "rule": "order-neq@1",
         "at": 1,
         "children": [
          {
           "rule": "order-farkas@1",
           "cuts": [],
           "literals": [
            [
             2,
             "-1"
            ],
            [
             3,
             "1"
            ],
            [
             4,
             "1"
            ]
           ],
           "final_cuts": []
          },
          {
           "rule": "order-farkas@1",
           "cuts": [],
           "literals": [
            [
             2,
             "1"
            ],
            [
             3,
             "-1"
            ],
            [
             4,
             "1"
            ]
           ],
           "final_cuts": []
          }
         ]
        }
       ]
      }
     }
    }
   },
   {
    "name": "N23-unemployment-order",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "lt",
      [
       "const",
       "bp",
       "unemployment_new_projection"
      ],
      [
       "const",
       "bp",
       "unemployment_old_projection"
      ]
     ]
    },
    "premises": [
     "n23u"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "87adbd2f65f1e24dafe94aaa912447cc79d36021b471268b7be69ca55d7a0816"
     ],
     "conclusion_meaning_id": "d79b8f798bd2750ea69f5f4debacc1db8576024aa06366d3f9f282b2df586d69",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "87d33be09bcbdedff27ca8af197a9bca1ee4b2ea280917caa75a6cad69982119"
      ],
      "conclusion_meaning_id": "d90470097b53676e6d489c36bdf9928674ffefac8353500af775d6692be1e667",
      "trace": {
       "rule": "expand",
       "at": 0,
       "children": [
        {
         "rule": "order-farkas@1",
         "cuts": [],
         "literals": [
          [
           1,
           "1"
          ],
          [
           2,
           "-1"
          ],
          [
           3,
           "1"
          ]
         ],
         "final_cuts": []
        }
       ]
      }
     }
    }
   },
   {
    "name": "news_consequences",
    "quantity": {
     "format": "ve-quantity@1",
     "formula": [
      "and",
      [
       "lt",
       [
        "const",
        "bp",
        "new_target_lower"
       ],
       [
        "const",
        "bp",
        "new_target_upper"
       ]
      ],
      [
       "and",
       [
        "lt",
        [
         "const",
         "bp",
         "projected_range_lower"
        ],
        [
         "const",
         "bp",
         "projected_range_upper"
        ]
       ],
       [
        "and",
        [
         "lt",
         [
          "const",
          "calendar_year",
          "projected_reach_year"
         ],
         [
          "const",
          "calendar_year",
          "projected_remain_year"
         ]
        ],
        [
         "and",
         [
          "eq",
          [
           "const",
           "bp",
           "statement_goal"
          ],
          [
           "const",
           "bp",
           "pledged_goal"
          ]
         ],
         [
          "and",
          [
           "lt",
           [
            "const",
            "bp",
            "pce_june_estimate"
           ],
           [
            "const",
            "bp",
            "pce_september_estimate"
           ]
          ],
          [
           "and",
           [
            "eq",
            [
             "add",
             "bp",
             [
              "const",
              "bp",
              "pce_september_estimate"
             ],
             [
              "scale",
              "bp",
              "-1",
              [
               "const",
               "bp",
               "pce_june_estimate"
              ]
             ]
            ],
            [
             "num",
             "bp",
             "10"
            ]
           ],
           [
            "and",
            [
             "le",
             [
              "decimal",
              "calendar_year",
              "2029"
             ],
             [
              "const",
              "calendar_year",
              "first_projected_target_year"
             ]
            ],
            [
             "and",
             [
              "eq",
              [
               "add",
               "bp",
               [
                "const",
                "bp",
                "growth_new_projection"
               ],
               [
                "scale",
                "bp",
                "-1",
                [
                 "const",
                 "bp",
                 "growth_old_projection"
                ]
               ]
              ],
              [
               "num",
               "bp",
               "10"
              ]
             ],
             [
              "and",
              [
               "eq",
               [
                "add",
                "bp",
                [
                 "const",
                 "bp",
                 "unemployment_old_projection"
                ],
                [
                 "scale",
                 "bp",
                 "-1",
                 [
                  "const",
                  "bp",
                  "unemployment_new_projection"
                 ]
                ]
               ],
               [
                "num",
                "bp",
                "20"
               ]
              ],
              [
               "lt",
               [
                "const",
                "bp",
                "unemployment_new_projection"
               ],
               [
                "const",
                "bp",
                "unemployment_old_projection"
               ]
              ]
             ]
            ]
           ]
          ]
         ]
        ]
       ]
      ]
     ]
    },
    "premises": [
     "N07-order",
     "N13-order",
     "N13-years",
     "N15-N24-same-goal",
     "N21-order",
     "N21-difference",
     "N22-year-lower-bound",
     "N23-growth-increase",
     "N23-unemployment-decrease",
     "N23-unemployment-order"
    ],
    "certificate": {
     "format": "ve-quantity-certificate@1",
     "environment_id": "ebe67b821ed0002cd02af7f55a0d3f4ac0017c8a72b5af652c0ba5aa44805a6a",
     "premise_meaning_ids": [
      "24c7b2345f47d515d56e99e90438a356e2b308b8aed1cf700bdf31296b424b5d",
      "9bd045422445381552b595ee5f5a2f44cf45608fd07eb22fab30c8d5014b6fb1",
      "7c60e976a1d0cdda401526a9f3c7209e0094d62167585b4ee0ab4f0a52925579",
      "57697ca9e5e718ee9d1ff85a8298e4dceadf4b690184af0ced92589bb8ce7a1d",
      "338aaac563e2da2148a74c801957720d5b717ddbe1cf11270ca9b299ea0abdb1",
      "eff7e11e1d3cb1fc3a4beeb41f56b59cb6bda7bc60421935fb1620c51a52c2ba",
      "285d116cd43b9ecac7973805beb0f117fabbf937ca66cbabf9180392c042bd8f",
      "bf3bd2518f4bd6775588027fc15913876e5953fa06dee8752b3415bba7d11e66",
      "0a2240fa7700e4885388a3467a11e5046dccc54e1e364602a152e714538cfde5",
      "d79b8f798bd2750ea69f5f4debacc1db8576024aa06366d3f9f282b2df586d69"
     ],
     "conclusion_meaning_id": "1936858647ed5728c0793b3ee48a4f5e8e9e49afdc16adce715ac52327cb1653",
     "core": {
      "checker_version": "ve-order-farkas-checker@1",
      "environment_id": "dfac2a2ca9ee72c1abb78f74df348b512d195e172fd39a56048432fba27c9bb9",
      "premise_meaning_ids": [
       "c2e6a14cb1987671a0aeaacd15673212fa0eabfdc0cb7ecd6c296e7dcb98a793",
       "44cd2de4d050a6f544c0b1479b4a75d732f6b5c4d08b8622d534e5cf84600204",
       "c187dc3d0ab020baca0c407475831169f67d786142a8470eef25c64d1faf74e3",
       "2447696f72adb5fe7d39db02e71beffc64bc5f7ee6b396db22d103eb794c54e5",
       "904c5a842f5a0785dee5709211674bd657b9108ae189ab3c3e9f04b7fe734833",
       "5a4c72f50a2b77ebfddc58e58295b27c2bc13756384b46c0255a74347cf95af1",
       "447b0a0a859bfd7a58f81f49134ed7cc0cbc0a127bfb517bb313f0aa0e4da110",
       "d3aaa0f62857fe811055bc45067badfbce3e3b71731ca0f27e67d4a443ff7445",
       "f3fe3f431cb95e0c1d8969eba47c5dd413b3e19c0ff779d9efa4154f77fc244b",
       "d90470097b53676e6d489c36bdf9928674ffefac8353500af775d6692be1e667"
      ],
      "conclusion_meaning_id": "8c949f6e05d7bafe02ffbb6b6e7c79e9028f034e1b15ac750358032b20b159ff",
      "trace": {
       "rule": "expand",
       "at": 10,
       "children": [
        {
         "rule": "close"
        },
        {
         "rule": "expand",
         "at": 11,
         "children": [
          {
           "rule": "close"
          },
          {
           "rule": "expand",
           "at": 12,
           "children": [
            {
             "rule": "close"
            },
            {
             "rule": "expand",
             "at": 13,
             "children": [
              {
               "rule": "close"
              },
              {
               "rule": "expand",
               "at": 14,
               "children": [
                {
                 "rule": "close"
                },
                {
                 "rule": "expand",
                 "at": 15,
                 "children": [
                  {
                   "rule": "close"
                  },
                  {
                   "rule": "expand",
                   "at": 16,
                   "children": [
                    {
                     "rule": "close"
                    },
                    {
                     "rule": "expand",
                     "at": 17,
                     "children": [
                      {
                       "rule": "close"
                      },
                      {
                       "rule": "expand",
                       "at": 18,
                       "children": [
                        {
                         "rule": "close"
                        },
                        {
                         "rule": "close"
                        }
                       ]
                      }
                     ]
                    }
                   ]
                  }
                 ]
                }
               ]
              }
             ]
            }
           ]
          }
         ]
        }
       ]
      }
     }
    }
   }
  ]
 }
}
---
# Source

**Document:** Reuters wire story, "Fed hikes rates, sees more tightening in search of 'timelier' drop in inflation" (also syndicated under the headlines "Fed raises rates in search of 'timelier' drop in inflation, sees more tightening ahead" and "Federal Reserve Raises Interest Rates Amid Persistent Inflation"), byline Howard Schneider, dateline WASHINGTON, Sept 16 (Reuters).

**URL:** https://www.reuters.com/ is the original wire source but returns HTTP 401 to automated/unauthenticated fetches (confirmed directly: `curl` against the reuters.com article URL returned `401`). The article is used here via its freely-readable syndicated republication, which carries the same byline, dateline, and body text verbatim: https://www.investing.com/news/economy-news/fed-hikes-rates-sees-more-tightening-in-search-of-timelier-drop-in-inflation-4904265 (published/updated "Sep 16, 2026, 02:02 PM" / "02:06 PM" per that page). Cross-checked against two further syndications with matching text: https://www.hawaiitribune-herald.com/2026/09/17/nation-world-news/fed-raises-rates-in-search-of-timelier-drop-in-inflation-sees-more-tightening-ahead/ and the NewsBreak mirror explicitly labelled "reuters-555486", https://www.newsbreak.com/reuters-555486/4890023219941-fed-raises-rates-in-search-of-timelier-drop-in-inflation-sees-more-tightening-ahead.

**Retrieval date:** 2026-09-21 (article published/dated 2026-09-16, five days earlier — within the "last two weeks" window).

**Licence / fair-use note:** This is copyrighted wire-service news copy, not public domain. Only the sentences formalised below are quoted, and the direct quotation is kept under the 120-word budget; the remainder is paraphrased in the numbered list below. The full syndicated copy (about 620 words) runs longer than the "about 300-500 words" guidance for the article as a whole; the twelve paragraphs formalised here (dropping a further "ALL EYES ON WARSH" section on midterm-election politics and mortgage rates, which adds no new fact type for this exercise) total 456 words, within range.

## Paraphrase and facts formalised (14 numbered sentences/clauses, source order)

1. The Federal Reserve raised interest rates on Wednesday, September 16, 2026, and signaled that further rate increases could come in the following months; new Fed chief Kevin Warsh joined a unanimous vote, which Reuters characterizes as an implicit acknowledgment that the Trump administration has not yet succeeded in controlling inflation.
2. President Trump had promised to lower prices; despite that, the combined effect of his tariffs, an energy-price shock from the start of the U.S.-Israeli war with Iran, and AI-driven capital spending kept inflation pressure high enough that the Fed judged a quarter-percentage-point rate increase necessary, taking the target range to 3.75%-4.00%.
3. New projections show 16 of the 18 FOMC policymakers expect at least one more quarter-point rate increase before the end of 2026, with only 2 of the 18 expecting rates to stay where they are.
4. Warsh again did not submit an individual rate projection ("dot") of his own.
5. This was the first policy change of Warsh's tenure; he took office in late May 2026 after Trump selected him, at the time expecting he would cut rates.
6. Contrary to that expectation, the new projections show the Fed opening the door to further tightening through next year, with the policy rate projected to reach the 4.00%-4.25% range by the end of 2026 and to remain there through the end of 2027.
7. The FOMC's policy statement said, quoted directly: "Today's policy action will support a timelier return to the Committee's 2% goal," issued after a two-day meeting.
8. The statement gave no forward guidance about future decisions, which is Warsh's preference; Reuters says this is likely to ease prior doubts that Warsh would avoid tightening policy out of deference to Trump.
9. The new statement dropped a reference, present in the previous statement, that had attributed elevated inflation partly to "supply shocks," which Reuters reads as a signal that policymakers (including Warsh) now see price pressures as broader-based.
10. Warsh is scheduled to hold a press conference starting at 2:30 p.m. EDT (18:30 GMT) to explain the decision further.
11. The Fed's new quarterly projections raised the estimate of PCE inflation to 3.7%, up from the 3.6% projected at the June 2026 meeting.
12. Inflation is now not projected to reach the Fed's 2% target until 2029 — a year later than previously expected.
13. Projected economic growth was raised slightly, from 2.2% to 2.3%; the projected year-end unemployment rate was lowered, from 4.3% to 4.1%.
14. Warsh has pledged, quoted directly, to bring inflation back to 2% "clearly and at sufficient speed" by raising rates as needed.

## Direct quotation (82 words: the two attributed statements, sentences 7 and 14 above, plus their immediate framing)

> WASHINGTON, Sept 16 (Reuters) - The Federal Reserve raised interest rates on Wednesday and flagged further increases in borrowing costs in coming months, with new U.S. central bank chief Kevin Warsh joining a unanimous decision... "Today's policy action will support a timelier return to the Committee's 2% goal," the central bank said in its policy statement after the end of a two-day meeting... Warsh has pledged to lower inflation back to 2% "clearly and at sufficient speed" by raising rates as needed.
