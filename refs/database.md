# Entities

## Knowledge Area
knowledge_areas
- id
- name
- relationship(knowledge_units)

## Knowledge Unit
knowledge_units
- id
- name
- relationship(knowledge_topics)
- relationship(knowledge_areas)

## Module
modules
- id
- name
- author
- date_added
- description
- notes
- relationship(knowledge_units/topics)
- relationship(files)

## File
files
- id
- name
- date_added

