from urllib.parse import urlencode, quote

"""
Helper functions for the Agent. 
"""


def expand_template(response, mappings):
    """
    Expands the template on the basis of the representation, i.e. Basic or Explicit. 

    :param response: Response obtained after hitting the base_url of collection

    :param mappings: Mappings of variables and values provided by the user to expand template 

    """
    # store all the required_props
    required_props = {}
    for prop in response['search']['hydra:mapping']:
        if prop['@type'] == 'hydra:IriTemplateMapping' and prop['hydra:required']:
            required_props[prop['hydra:variable']] = True

    # check if any required_prop is missing from mappings and throw error if there are any
    for key in required_props:
        if key not in mappings:
            raise KeyError(
                "{} is required but is missing from filters".format(key))

    # extract the url from the template so that url can be constructed:

    # --- Ideally should be called like this but gives error right now due to wrong template ----

    # base_template = ""
    # template = response['search']['hydra:template']
    # start_index_para = template.find('(')
    # end_index_para = template.find(')')
    # if start_index_para != 1 and end_index_para != -1:
    #     base_template = template[:start_index_para]

    # check the type of Representation.
    # Hydra Supports two types of Representations: BasicRepresentation or ExplicitRepresentation.
    if response['search']['hydra:variableRepresentation'] == 'hydra:BasicRepresentation':
        # Expansion using Basic Representation
        query_string = urlencode(mappings, quote_via=quote, safe='')
        # append to the end of url
        url = response['@id'] + '?' + query_string
        return url

    if response['search']['hydra:variableRepresentation'] == 'hydra:ExplicitRepresentation':
        # Expansion using Explicit Representation.
        # Used when used with JSON-LD format so that tagging with "@language", "@type", or an "@id"
        """
        The ExplicitRepresentation includes type and language information and differentiates between IRIs and literals by serializing values as follows:
        * IRIs are represented as-is.
        * Literals, i.e., (typed) values and language-tagged strings are represented by their lexical form, surrounded by a single pair of doubles quotes (").
        * If a literal has a language, a single @ symbol is appended after the double-quoted lexical form, followed by a non-empty [BCP47] language code.
        * If a literal has a type, two caret symbols (^^) are appended after the double-quoted literal, followed by the full datatype IRI.
        """
        modified_mapping = {}
        for prop, value in mappings.items():
            # check if its an iri
            if '@id' in value:
                encoded_iri = quote(value['@id'], safe='')
                modified_mapping[prop] = encoded_iri
                continue
            # if language is provided
            if '@value' in value and '@language' in value:
                expand_value = '\"' + \
                    value['@value'] + '\"' + '@' + value['@language']
                modified_mapping[prop] = quote(expand_value, safe="")
                continue
            # if it's a typed value
            if '@value' in value and '@type' in value:
                expand_value = '\"' + \
                    value['@value'] + '\"' + '^^' + value['@type']
                modified_mapping[prop] = quote(expand_value, safe='')
                continue
            # if it's a normal string literal
            if value is not None:
                expand_value = '\"' + value + '\"'
                modified_mapping[prop] = quote(expand_value, safe='')
                continue

        query_string = urlencode(modified_mapping, safe='%')
        url = response['@id'] + '?' + query_string
        return url
