# -*- coding: utf-8 -*-

"""Utils to be used in notebooks"""

from collections import defaultdict
from functools import lru_cache
from typing import Set, Tuple, Any, Dict

import networkx as nx
import obonet
from tqdm import tqdm


@lru_cache(maxsize=None)
def get_ncbiontology():
    """Wrapper to get the ncbiontology."""
    return obonet.read_obo(
        'http://purl.obolibrary.org/obo/ncbitaxon.obo'
    )


def get_genus_and_family_info_for_plants(
    plant_ids: Set[str]
) -> Tuple[Dict[Any, list], Dict[Any, list]]:
    """Return dictionaries mapping plant species to their genus/families."""
    # Load ncbitaxon taxonomy. This might take a couple of mins
    ncbitaxon_ontology = get_ncbiontology()

    # Get the childs of Viridiplantae (all plants)
    plant_childs = nx.ancestors(ncbitaxon_ontology, 'NCBITaxon:33090')

    # Subset the graph to make it faster to the relevant part (plants only)
    ncbitaxon_ontology = ncbitaxon_ontology.subgraph(plant_childs).copy()

    # Relabel nodes to be consistent with the dataset
    ncbitaxon_ontology = nx.relabel_nodes(
        ncbitaxon_ontology,
        {
            node: node.replace('NCBITaxon:', 'ncbitaxon:').strip()
            for node in ncbitaxon_ontology.nodes()
        },
    )

    family_nodes = set()
    genus_nodes = set()

    # Identify the famlies and genus nodes
    for id_, data in ncbitaxon_ontology.nodes(data=True):

        if 'property_value' not in data:
            continue

        # Group edges based on the different taxonomic levels of interst
        for value in data['property_value']:
            if value == 'has_rank NCBITaxon:family':
                family_nodes.add(id_)
            elif value == 'has_rank NCBITaxon:genus':
                genus_nodes.add(id_)

    genus_to_species = defaultdict(list)
    family_to_species = defaultdict(list)

    # Build groups for each family
    for node in tqdm(family_nodes, desc='order family'):
        children = set(nx.ancestors(ncbitaxon_ontology, node))

        for child in children:

            # Check plant is one of the ones in the dataset
            if child not in plant_ids:
                continue

            family_to_species[node].append(child)

    # Build groups for each genus
    for node in tqdm(genus_nodes, desc='order genus'):
        children = set(nx.ancestors(ncbitaxon_ontology, node))

        for child in children:

            # Check plant is one of the ones in the dataset
            if child not in plant_ids:
                continue

            genus_to_species[node].append(child)

    return genus_to_species, family_to_species
