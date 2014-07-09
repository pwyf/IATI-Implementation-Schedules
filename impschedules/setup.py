from impschedules import app, models, db, properties

def setup():
    db.create_all()
    # create user
    username = "admin"
    password = app.config["ADMIN_PASSWORD"]
    admin = 1
    u = models.ImpSchedUser(username,password,admin)
    db.session.add(u)
    db.session.commit()

    # create alterationcategories
    for k, v in properties.change_reasons.items():
        ac = models.AlterationCategory()
        ac.name = k
        ac.description = v
        ac.longdescription = ""
        db.session.add(ac)
    db.session.commit()

    # create publishers

    for publisher in properties.publishers:
        p = models.Publisher()
        p.publisher_actual = publisher["name"]
        p.publisher_original = publisher["name"]
        p.publisher_code_actual = publisher["code"]
        p.publisher_code_original = publisher["code"]
        db.session.add(p)
    db.session.commit()
    
    # create properties
    attributes = {'notes': {}, 'status_category': {}, 'publication_date': {}, 'exclusions': {}}
    elementgroups = properties.elementgroups
    
    for elementgroup, values in elementgroups.items():
        eg = models.ElementGroup()
        eg.name = elementgroup
        eg.description = values["description"]
        eg.order = values["order"]
        db.session.add(eg)
    db.session.commit()

    elementgroups = db.session.query(
                    models.ElementGroup.id,
                    models.ElementGroup.name
                    ).all()
    elementgroups = dict(map(lambda x: (x[1],x[0]), elementgroups))

    elements = properties.elements
    for level, values in elements.items():
        for element, elvalue in values.items():
            e = models.Element()
            e.name = element
            e.level = level
            e.elementgroup = elementgroups[elvalue["group"]]
            if (elvalue.has_key("description")):
                e.description = elvalue["description"]
                e.order = elvalue["order"]
            db.session.add(e)
            db.session.commit()
            element_id = e.id
            if (elvalue.has_key("defining_attribute")):
                # if there are multiple versions of this element, e.g. funding, extending participating-orgs
                for defining_attribute_value, property_values in elvalue["defining_attribute_values"].items():
                    #for attribute in attributes:
                    p = models.Property()
                    p.level = level
                    p.parent_element = element_id
                    #p.attribute = attribute
                    p.defining_attribute = elvalue["defining_attribute"]
                    p.defining_attribute_value = defining_attribute_value
                    p.defining_attribute_description = property_values['description']
                    p.order = property_values['order']
                    db.session.add(p)
            else:
                #for attribute in attributes:
                p = models.Property()
                p.level = level
                p.parent_element = element_id
                #p.attribute = attribute
                db.session.add(p)
    db.session.commit()
    return 'Setup. <a href="/import">Import</a> XML files?'
