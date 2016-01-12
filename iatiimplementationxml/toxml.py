# Copyright (C) 2012 Ben Webb <bjwebb67@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Some additions to support new common standard implementation schedules
# by Mark Brough <mark.brough@publishwhatyoufund.org>

# This program can be run at the command line, or as a module. 

import xlrd
from lxml.builder import ElementMaker
import lxml.etree as etree
import datetime
import string

# Multiple structures are supported, and are imported as "structure".

datemode = None
def get_date(value):
    """ Helper function to return the xml date string for a given
        spreadsheet cell value.
    
    """
    global datemode
    try:
        date = datetime.datetime(*xlrd.xldate_as_tuple(value, datemode))
        if (str(date) == "1905-07-07 00:00:00"):
            raise TypeError
        return date.date().isoformat()
    except ValueError:
        return ''
    # Unfortunately properly formatted dates are not required in the CS implementation schedule. Allow this for now, deal with it later.
    except TypeError:
        try:
            if (value.startswith("number:")):
                value = value.strip("number:")
                value = str(int(value))
        # It's a float
        except AttributeError:
            value = str(int(value))
        if (len(value) == 4):
            # If the length is 4, it's probably a year
            try:
                thedate = datetime.datetime.strptime(value, "%Y")
                datefix = datetime.timedelta(days=364.25)
                thedate = thedate + datefix
                return (thedate.date().isoformat())
            except ValueError:
                return value
        elif (value.isdigit()):
            value = int(value)
            try:
                thedate = datetime.datetime.strptime(value, "%Y")
                datefix = datetime.timedelta(days=364.25)
                thedate = thedate + datefix
                return (thedate.date().isoformat())
            except ValueError:
                return value
        else:
            return ""

def datetimestamp():
    """ Helper function to produce a nice ISO string for the current date
        and time.

    """
    """
        Exclude GuessTimezone for now - not working under GMT. Changed to uctnow() below
    class GuessTimezone(datetime.tzinfo):
        def utcoffset(self, dt):
            td = datetime.datetime.now() - datetime.datetime.utcnow()
            return datetime.timedelta(hours=round(td.seconds/3600.0),
                                      minutes=(round(td.seconds/60.0))%60)
        def dst(self, dt):
            return datetime.timedelta(seconds=0) 
    """

    # Line below was now = datetime.datetime.now(GuessTimezone)
    now = datetime.datetime.utcnow()
    now -= datetime.timedelta(microseconds=now.microsecond)
    return now.isoformat()

def use_code(heading, text, codes=None):
    if (codes == None):
        codes = structure.codes
    """ Helper function to return the short code for a given heading
        and text value.

    """
    if heading in codes:
        if text == '': return ''
        try:
            return codes[heading][text]
        except KeyError:
            raise Exception("Error finding code '" + text + "' under '" + heading + "' in your structure. You may be using a different version of the template.")
            pass
    else:
        return text


def parse_data(root, sheet, rows):
    """ Parse a 'data' sheet.
        ie. Activity Data or Organisation Data

        root -- an xml element to append to
        sheet -- the xlrd sheet element to parse
        rows -- a list of xml tags that correspond to each row
        
    """
    for rowx,rowname in enumerate(rows):

        if rowname == '':
            continue

        createelements = []
        
        # this is to work with elements that are divided in later versions of the schedule: create 2 identical elements based on values provided in schedule.
        if (rowname[1] == '2-type'):
            xelement = {'element': rowname[0],
                        'type': rowname[2]}
            createelements.append(xelement)

            xelement = {'element': rowname[0],
                        'type': rowname[3]}
            createelements.append(xelement)

        elif isinstance(rowname, tuple):
            xelement = {'element': rowname[0],
                        'type': rowname[2]}
            createelements.append(xelement)
        else:
            xelement = {'element': rowname}
            createelements.append(xelement)

        for theelement in createelements:
            rowxml = etree.SubElement(root, theelement["element"])
            if theelement.has_key("type"):
                rowxml.attrib['type'] = theelement["type"]
            
        
            for colx, heading in enumerate(structure.header):
                if heading == '':
                    continue
                try:
                    cell = sheet.cell_value(rowx=rowx, colx=colx)
                except IndexError:
                    continue
                if heading in structure.codes_activity:
                    el = etree.SubElement(rowxml, heading)
                    if heading == 'exclusions':
                        narrative_el = etree.SubElement(el, 'narrative')
                        narrative_el.text = unicode(cell)
                        try:
                            attrib_cell = unicode(sheet.cell_value(rowx=rowx, colx=colx+1))
                        except IndexError:
                            continue
                    else:
                        attrib_cell = cell
                    if attrib_cell == '':
                        continue
                    else:
                        el.attrib['category'] = use_code(heading,
                                            unicode(attrib_cell),
                                            codes=structure.codes_activity)
                else:
                    if heading in structure.date_tags:
                        cell = get_date(cell)
                    else:
                        cell = unicode(cell)
                    if cell != '':
                        el = etree.SubElement(rowxml, heading)
                        el.text = cell
    return root


def parse_information(root, sheet, rows, schedule_date):
    """ Parse the Publisher Information sheet

        root -- an xml element to append to
        sheet -- the xlrd sheet element to parse
        rows -- a list of tuples containing structural
                information about each cell in the sheet 

        Below: rowx = number of the row from structure (i.e., where should this data be found in the sheet)
               row = row data from structure (i.e., what data should be in this sheet)
               row_data = data from the sheet for this particular value of rowx

    """
    for rowx,row in enumerate(rows):
        if row:
            el = etree.SubElement(root, row[1])
            narrative_el = etree.SubElement(el, 'narrative')
            row_data = sheet.row(rowx)
            try:
                if row[4] == 'narrative':
                    for i in 2,3:
                        if row[i] != '':
                            if row[i] in structure.date_tags:
                                d = get_date(row_data[i].value)
                                if d != '':
                                    el.attrib[row[i]] = d
                            else:
                                el.attrib[row[i]] = use_code(row[i],
                                        unicode(row_data[i].value))
                    narrative_el.text = row_data[4].value
                else:
                    narrative_el.text = "".join(map(lambda x: x.value, row_data[2:4]))
            except IndexError:
                pass
            # This is to work with CS implementation schedules. Item 0 in row contains the number of the column to get information from in the schedule; item 1 contains the element; item 2 contains the attribute
            try:
                if (type(row[0]) == int):
                    if row[2] in structure.date_tags:
                        el.attrib[row[2]] = get_date(row_data[row[0]].value)
                    else:
                        if (row[2] != ''):
                            el.attrib[row[2]] = row_data[row[0]].value
                        else:
                            narrative_el.text = row_data[row[0]].value
            except IndexError:
                pass
            # This is to work with CS implementation schedules. "Split" allows attributes to be provided across multiple rows.
            try:
                if (row[0] == 'split'):
                    for attribute, param in row[2].items():
                        col = param["col"]
                        if param.has_key("row"):
                            which_row = sheet.row(param["row"]+rowx)
                        else:
                            which_row = row_data
                        for cell, values in param["opts"].items():
                            notpresent = ["", "no", "NO"]
                            if ((which_row[param["col"]+cell].value.strip()) not in notpresent):
                                el.attrib[attribute] = use_code(attribute, values)
                                break
                            else:
                                el.attrib[attribute] = ""

                if (row[0] == 'split-pub'):
                    dataa = row_data[2].value
                    datab = row_data[10].value
                    if ((dataa != "") and (dataa !="no") and (dataa != "NO")):
                        # return schedule date, if the box looks like it's probably ticked
                        el.attrib[row[2]] = schedule_date
                    else:
                        el.attrib[row[2]] = get_date(row_data[10].value)          

                if (row[0] == 'split-pub2'):
                    el.attrib[row[2]] = get_date(row_data[10].value)  


                if (row[0] == 'split-scope'):
                    el.attrib['scope'] = ''
                    narrative = ''
                    for attribute, param in row[2].items():
                        narrative = narrative + (attribute.capitalize()) + ": "
                        # attribute is current or future
                        # set starting row
                        if param.has_key("row"):
                            which_row = param["row"]+rowx
                        else:
                            which_row = rowx-1 # not sure why -1, but it works
                        for i in range(0,3):
                            row = which_row + i
                            col = param["col"]
                            the_row = sheet.row(row)
                            if (the_row[col].value == ''):
                                break
                            elif (i>0):
                                narrative = narrative + "; "
                            try:
                                scope_value = int(the_row[col+6].value*100)
                            except ValueError:
                                scope_value = ""
                            narrative = narrative + the_row[col].value + " (" + str(scope_value) + "%)"
                            if ((attribute == 'future') and (the_row[col+5].value!='')):
                                narrative = narrative + " by " + get_date(the_row[col+5].value)
                        if (attribute == 'current'):
                            if (narrative == 'Current: '):
                                narrative = ""
                            else:
                                narrative = narrative + "; "
                    narrative_el.text = narrative
            except IndexError:
                pass
    return root
    

def silent_value(sheet, **args):
    """ Helper function to fetch cell values and convert them to strings,
        whilst ignoring possible exceptions (ie. if a cell does not exist).

        Also make sure all values are returned as unicode, and that integers
        are formatted correctly. 

    """
    try:
        value = sheet.cell_value(**args)
        if isinstance(value, float):
            if value == round(value):
                return unicode(int(value))
            else:
                return unicode(value)
        else:
            return value
    except IndexError:
        return ''


def full_xml(spreadsheet, s):
    """ Print the full parsed xml for the given spreadsheet filename"""
    global structure
    structure = __import__(s, fromlist=[''])
    global datemode
    global E
    E = ElementMaker()
    book = xlrd.open_workbook(spreadsheet)
    datemode = book.datemode
    sheet = book.sheet_by_index(structure.structure["metadata"])

    # TODO Add handling of proper excel dates

    try:
        datestring = get_date(sheet.cell_value(rowx=structure.metadata["date"]["row"], colx=structure.metadata["date"]["col"]))
    except TypeError:
        print "type error!"
        datestring = ""
    except ValueError:
        print "Value Error: are your dates properly formatted?"
        datestring = ""

    # TODO Make default language configurable
    root = lang("en", E.implementation(
        E.metadata(
            E.publisher(
                silent_value(sheet, rowx=structure.metadata["name"]["row"], colx=structure.metadata["name"]["col"]),
                code=silent_value(sheet, rowx=structure.metadata["code"]["row"], colx=structure.metadata["code"]["col"])
            ),
            E.version(silent_value(sheet, rowx=structure.metadata["version"]["row"], colx=structure.metadata["version"]["col"])),
            E.date(datestring),
            E.schedule_type(
                structure.identification["name"],
                code= structure.identification["code"]
            )
        ),
        parse_information(
            E.publishing(),
            book.sheet_by_index(structure.structure["publishing"]),
            structure.publishing_rows,
            datestring # provide date of implementation schedule; some answers can be e.g. "already published" which means the date of schedule.
        ),
        parse_data(
            E.organisation(),
            book.sheet_by_index(structure.structure["organisation"]),
            structure.organisation_rows
        ),
        parse_data(
            E.activity(),
            book.sheet_by_index(structure.structure["activity"]),
            structure.activity_rows
        )
    ))
    root.set('generated-datetime', datetimestamp())
    return root

def documentation_from_dict(codes):
    """ Produces a documentation table from a dict that maps codes. """
    # Create an ElementMaker for creating html tags
    HE = ElementMaker(namespace="http://www.w3.org/1999/xhtml",
                     nsmap={'xs':"http://www.w3.org/2001/XMLSchema",
                            'xml':"http://www.w3.org/XML/1998/namespace",
                            'xhtml':"http://www.w3.org/1999/xhtml"})
    table = HE.table()
    table.append( HE.tr( HE.th('Text'), HE.th('Code') ) )
    for text, code in sorted(codes.items()):
        row = HE.tr( HE.td(text), HE.td(code) )
        row.tail = '\n'
        table.append( row )
    return HE.div('The value of this attribute should be one of the codes listed below:\n', table)

def sheetschema(root, sheetname):
    """ Produce the schema elements for the named sheet.

        root -- an xml element to append to
        sheetname -- the short name of a sheet, as used in the structure
                     data and as the xml tag name.
                     Possible values are 'activity' and 'organisation'

    """
    global E
    rows = vars(structure)[sheetname+'_rows'] 
    docs = vars(structure)[sheetname+'_docs']
    #tuple_rows_done = {}
    ann = {
        "activity": """
        Contains information about the data provider's plans to implement
        specific parts of the activity data.

        Each of the child elements if either an informationArea, or a
        list of informationAreas.

        """, "organisation":"""
        Contains information about the data provider's plans to implement
        specific parts of the organisation data.

        """
    }
    choice_el = E.choice(maxOccurs="unbounded")
    root.append(
        E.element(
            E.annotation(lang("en", E.documentation(ann[sheetname]))),
            E.complexType(
                choice_el
            ),
            name=sheetname
        )
    )
    tuple_rows_done = {}
    for rowx,rowname in enumerate(rows):
        element = None
        if isinstance(rowname, tuple):
            if rowname[0] in tuple_rows_done:
                restriction_type = tuple_rows_done[rowname[0]]
            else:
                restriction_type = E.restriction(base="xs:string")
                tuple_rows_done[rowname[0]] = restriction_type
                element = E.element(
                    E.complexType(
                        E.complexContent(
                            E.extension(
                                E.attribute(
                                    E.annotation(lang("en",E.documentation(
                                        """The type of information reported about this element,
                                        see restriction for details."""
                                    ))),
                                    E.simpleType(
                                        restriction_type
                                    ),
                                    name="type"
                                ),
                                base="informationArea"
                            )
                        ),
                    ),
                    name=rowname[0]
                )
                choice_el.append(element)
            restriction_type.append(E.enumeration(value=rowname[2]))
        elif rowname:
            element = E.element(name=rowname, type="informationArea")
            choice_el.append(element)
        if element is not None and docs[rowx]:
            element.insert(
                0,
                E.annotation(lang("en", E.documentation(docs[rowx])))
            )

def publishingschema(root):
    """ Produce the necessary schema elements for the publishing sheet. 

        root -- an xml element to append to

    """
    global E
    rows = structure.publishing_rows
    docs = structure.publishing_docs
    all_el = E.all()
    root.append(
        E.element(
            E.annotation(lang("en", E.documentation("""
            Contains information about when and how data will be
            published, including any general exceptions.

            All child elements may only contain text, but may also have
            attributes.

            """))),
            E.complexType(all_el),
            name="publishing"
        )
    )
    for rowx,row in enumerate(rows):
        if row:
            if row[4] == "narrative":
                ext = E.extension(base="narrativeParent")
                el = E.element(
                    E.complexType(
                        E.complexContent(
                            ext
                    ) ),
                    name=row[1],
                    minOccurs="0"
                )
                for i in 2,3:
                    if row[i] != '':
                        if row[i] in structure.date_tags:
                            t = "xs:date"
                        elif row[i] in structure.decimal_tags:
                            t = "xs:decimal"
                        else:
                            t = "xs:string"
                        attribute = E.attribute(name=row[i],
                            type=t)
                        ext.append(attribute)
                        try:
                            try:
                                dfd = documentation_from_dict(structure.codes[row[i]])
                            except KeyError:
                                dfd = ''
                            attribute.insert(0,
                                E.annotation(lang("en", E.documentation(
                                    docs[rowx][i-1],
                                    dfd
                                )))
                            )
                        except IndexError:
                            pass


            else:
                el = E.element(name=row[1], type="narrativeParent")
            if docs[rowx]:
                if isinstance(docs[rowx], tuple):
                    documentation = docs[rowx][0]
                else:
                    documentation = docs[rowx]
                el.insert(0,
                    E.annotation(lang("en", E.documentation(documentation)))
                )
            all_el.append(el)

def lang(code, el):
    """ Helper function to add language code to an element, since
        Elementmaker syntax does not support namespaces.

    """
    el.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = code
    return el


def full_schema(s):
    """ Print the full schema, based on the definitions in structure.py"""

    global structure
    structure = __import__(s, fromlist=[''])
    global E
    E = ElementMaker(namespace="http://www.w3.org/2001/XMLSchema",
                     nsmap={'xs':"http://www.w3.org/2001/XMLSchema",
                            'xml':"http://www.w3.org/XML/1998/namespace",
                            'xhtml':"http://www.w3.org/1999/xhtml"})
    headerchoice = E.choice(maxOccurs="unbounded", minOccurs="0")
    root = E.schema(
        # Different syntax to avoid clash with python's import statement
        etree.Element("{http://www.w3.org/2001/XMLSchema}import",
            {'namespace':"http://www.w3.org/XML/1998/namespace",
            'schemaLocation':"xml.xsd"}),
        E.annotation(lang("en", E.documentation("""
        International Aid Transparency Initiative: Implementation
        This file autogenerated {} 

        This W3C XML Schema defines an XML document type for an
        Implementation Schedule of an IATI data provider.

        """.format(datetimestamp())))),
        E.complexType( 
            E.annotation(lang("en", E.documentation("""
            Type that corresponds to a row of the Activity or Organsation
            spreadsheets. Describes the implementation of a specific
            field, or type of information by the data provider.

            """))),
            headerchoice,
            name = "informationArea"
        ),
        E.element(
            E.annotation(lang("en", E.documentation("""
            Top level element containg elements for each of the top level
            types of information found in the implementation schedule.

            """))),
            E.complexType(
                E.all(
                    E.element(ref="metadata"),
                    E.element(ref="publishing"),
                    E.element(ref="organisation"),
                    E.element(ref="activity"),
                ),
                E.attribute(
                    E.annotation(lang("en", E.documentation("""
                    ISO 2 letter code specifying the default language for text in this implementation schedule.

                    """))),
                    ref="xml:lang"),
                E.attribute(
                    E.annotation(lang("en", E.documentation("""
                    The datetime that the xml file was generated.
                    (NOT the date that the schedule was written)

                    """))),
                    name="generated-datetime", type="xs:dateTime")
            ),
            name="implementation"
        ),
        E.element(
            E.annotation(lang("en", E.documentation("""
            Various metadata about the implementation schedule.

            """))),
            E.complexType(
                E.choice(
                    E.element(
                        E.annotation(lang("en", E.documentation("""
                        The publisher that this is a schedule for.
                        The code should be the IATI organisation identifier.
                        
                        """))),
                        name="publisher", type="codeType"),
                    E.element(
                        name="version", type="textType"),
                    E.element(
                        E.annotation(lang("en", E.documentation("""
                        The date when the implementation schedule was last updated.

                        """))),
                        name="date", type="xs:date"),
                    minOccurs="0", maxOccurs="unbounded"
                ),
            ),
            name="metadata"
        ),
        E.element(
            E.annotation(lang("en", E.documentation("""
            Element for enclosing long pieces of human readable text, in
            order to allow multiple translations whilst retaining the
            uniqueness of the parent object.

            """))),
            type="textType",
            name="narrative"
        ),
        E.complexType(
            E.annotation(lang("en", E.documentation("""
            Type for elements that may contain one or more narrative
            elements. Thus this element can be unique, and contain text
            in multiple languages. 

            """))),
            E.choice(
                E.element(ref="narrative"),
                maxOccurs="unbounded",
                minOccurs="0"
            ),
            name="narrativeParent"
        ),
        E.complexType(
            E.annotation(lang("en", E.documentation("""
            Type for elements that contain a string, but also have a code
            attribute. 

            """))),
            E.simpleContent(
                E.extension(
                    E.attribute(name="code", type="xs:string"),
                    base="textType"
                )
            ),
            name="codeType"
        ),
        E.complexType(
            E.annotation(lang("en", E.documentation("""
            Type for elements containing human readable text. Supports
            the xml:lang attribute in order to indicate the language of
            the text. Any element of this type should be repeatable in
            order to provide multiple translations within one xml
            document.

            If no language is indicated, the value specified by the root
            element is used.

            """))),
            E.simpleContent(
                E.extension(
                    E.attribute(ref="xml:lang"),
                    base="xs:string"
                )
            ),
            name="textType"
        )
    )
    for i, heading in enumerate(structure.header):
        if heading == '': continue
        if heading in structure.codes_activity: 
            complexType = E.complexType( 
                E.attribute(
                    E.annotation(lang("en", E.documentation(
                        documentation_from_dict(structure.codes_activity[heading])
                    ))),
                    name="category",
                    type="xs:string"
                )
            )
            if heading == 'exclusions':
                complexType.insert(0, E.choice(
                    E.element(
                        name="narrative",
                        type="textType"),
                    maxOccurs="unbounded"
                ) ) 
            headerchoice.append(
                E.element( 
                    E.annotation(lang("en", E.documentation(structure.header_docs[i]))),
                    complexType,
                    name=heading
                ),
            )
        else:
            if heading in structure.date_tags:
                t = "xs:date"
            else:
                t = "textType"
            headerchoice.append(E.element(
                E.annotation(lang("en", E.documentation(structure.header_docs[i]))),
                name=heading,
                type=t,
                minOccurs="0"))
    sheetschema(root, 'organisation')
    sheetschema(root, 'activity')
    publishingschema(root)
    return root

# This function opens the sheet, looks for a defining pattern of the structure, and returns a structure
def detect_structure(filename):
    from iatiimplementationxml.structures import patterns
    # open workbook

    book = xlrd.open_workbook(filename)

    # look for distinct pattern
    for s,p in patterns.structures.items():
        try:
            sheet = book.sheet_by_index(p["sheet"])
            value = sheet.cell_value(rowx=(p["row"]-1), colx=(p["col"]-1))
            if (value.strip() == p["value"]):
                structure = s
                break
        except IndexError:
            pass
    try:
        return structure
    except UnboundLocalError:
        raise Exception("Sorry, your schedule does not appear to conform to any known structure.")

# This function can be used to convert a schedule when this is 
# used as a module, e.g.:
#   import toxml
#   toxml.convert_schedule(PATH_TO_THE_SCHEDULE, STRUCTURE_OF_THE_SCHEDULE)

def convert_schedule(filename, s):
    if (s == "detect"):
        s = detect_structure(filename)
    xml = full_xml(filename, "iatiimplementationxml.structures." + s)
    return etree.tostring(xml,
        xml_declaration=True,
        encoding="utf-8")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        if sys.argv[2].startswith("--structure="):
            s = sys.argv[2]
            s = s.replace("--structure=", "")
            if (s == ""):
                print """
        Error:
        No structure provided. Remove --structure option to default 
        to IATI Standard template or provide a structure."""
                exit()
        else:
            s = "structure"
    else:
        s = "structure"
    s = "structures."+s
    if len(sys.argv) > 1:
        if sys.argv[1] == "--schema":
            xml = full_schema(s)
        else:
            xml = full_xml(sys.argv[1], s)
        print etree.tostring(xml,
                             pretty_print=True,
                             xml_declaration=True,
                             encoding="utf-8")
    else:
        print """Usage:
        python toxml.py --schema    -- Generates the XML schema 
        python toxml.py [filename]  -- Assumes the file is xls and tries
                                       to generate xml from it"""
