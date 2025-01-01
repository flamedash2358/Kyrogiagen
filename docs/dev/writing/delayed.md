# DelayedEvents

## What is a Delayed Event?

Delayed events are special event blocks that can be added to the ShortEvent and Patrol formats. They allow the writer to specify a ShortEvent to be **triggered** by the originating event. These are called delayed events because their appearance can be delayed by a certain number of moons.

Throughout this documentation we will refer to the DelayedEvent format block as the "delayed event" and the event that is *chosen to eventually display* as the "triggered event". The event that the delayed event is contained within will be referred to as the "parent event".

## DelayedEvent Format

```json
"delayed_event": [
        {
        "event_type": "",
        "pool": {},
        "moon_delay": [1,1],
        "involved_cats": {}
        }
    }
]
```

This block can be added to the end of ShortEvent and Patrol formats.

!!! note
    The delayed event block is a *list*, this means that you could have multiple delayed event dictionaries contained within, each dictionary creating it's own triggered event.

### event_type:str

Specify which ShortEvent type the triggered event will be. 

> * death
* injury
* new_cat
* misc

!!! note
    Keep in mind that you can only choose one event type, so you cannot add events from multiple event types into the pool.

### pool:dict[list]

You can specify a whole pool of events to be chosen from. Only one event from this pool will be chosen as the triggered event. You can specify by `subtype`, `event_id`, or `excluded_event_id`. You do not need to include every parameter, but you must utilize at least one.

!!! important
    You **cannot** specify both `subtype` *and* `event_id`. 
    You **can** specify both `subtype` *and* `excluded_event_id`.

```json
        "pool": {
            "subtype": []
            "event_id": []
            "excluded_event_id": []
        },
```

| Parameter           | Use                                                                    |
|---------------------|------------------------------------------------------------------------|
| `subtype`           | Events to be added to the pool will contain *all* subtypes specified.  |
| `event_id`          | Only events with the specified event_ids will be added to the pool.    |
| `excluded_event_id` | All events with the specified event_ids will be removed from the pool. |


### moon_delay:tuple[int]

This specifies how many moons must pass before the triggered event appears. Writers are able to specify a range `[x, y]` with `x` being the smallest possible delay and `y` being the largest possible delay.  One number will be picked between `x` and `y` to serve as the delay.  

### involved_cats:dict[str, dict]

This specifies what cats can fill the roles within the triggered event. You can also use this to carry cats from the parent event into the triggered event. This is structured as a dictionary, with the **key** being the triggered event's cat role and the **value** being either a dictionary of constraints or a parent event's cat role.

Example of how this looks in use, the parent event for this hypothetical event is a murder event:
```json linenums="1"
    "involved_cats": {
        "m_c": "r_c",
        "mur_c": "m_c", 
        "r_c": { 
            "age": ["any"] 
        }
    }
```
**"m_c": "r_c",**
> r_c is the random cat from the parent event. They will be m_c, or the main cat, in the triggered event. 

**"mur_c": "m_c"**
> m_c is the main cat from the parent event. They will be mur_c, or the murdered cat, in the triggered event.

**"r_c": {}**
> In this line, we aren't carrying over any cat from the parent event. Instead, we're trying to find a new cat. We're okay with this being any cat currently existing, so we just set the `age` constraint to `any`. A cat will be chosen from the currently living cats, excluding any cats already involved in this event.

The cat constraints that can be utilized here are the same as [ShortEvents](shortevents.md#r_cdictstr-various), with a few exclusions. The ***only*** constraints you *can* use are `age`, `status`, `skill`, `trait`, and `backstory`.

## Example

Here's an example of a delayed event being utilized for a murder event.

```json
    {
        "event_id": "gen_death_murder_any1",
        "location": [ "any" ],
        "season": [
            "any"
        ],
        "sub_type": ["murder"],
        "tags": [],
        "weight": 20,
        "event_text": "m_c was murdered. The culprit is unknown.",
        "m_c": {
            "status": [
                "kitten",
                "apprentice",
                "warrior",
                "deputy",
                "medicine cat apprentice",
                "medicine cat",
                "mediator apprentice",
                "mediator",
                "elder"
            ],
            "dies": true
        },
        "r_c": {
            "age": ["adolescent", "young adult", "adult", "senior adult"],
            "status": [ "any" ]
        },
        "history": [{
            "cats": ["m_c"],
            "reg_death": "m_c was secretly murdered by r_c."
        }],
        "relationships": [
            {
                "cats_from": [
                    "r_c"
                ],
                "cats_to": [
                    "m_c"
                ],
                "values": [
                    "platonic"
                ],
                "amount": -15
            },
            {
                "cats_from": [
                    "r_c"
                ],
                "cats_to": [
                    "m_c"
                ],
                "values": [
                    "dislike"
                ],
                "amount": 15
            }
        ],
        "delayed_event": [
                {
                "event_type": "misc",
                "pool": {
                    "subtype": ["murder_reveal"]
                },
                "moon_delay": [1,10],
                "involved_cats": {
                    "m_c": "r_c",
                    "mur_c": "m_c",
                    "r_c": {
                        "age": ["any"]
                    }
                }
            }
        ]
    },
```