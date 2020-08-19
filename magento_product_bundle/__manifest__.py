{   # pylint: disable=C8101,C8103
    'name': "Magento Product Bundle",

    'summary': "Trata o tipo de produto 'bundle' como configurado.",

    'description': "",
    'author': "Goiaba Intelligence",
    'website': "",
    'category': 'Uncategorized',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Mackilem Van der Laan <mack.vdl@gmail.com>',
    ],
    'depends': ['product', 'connector_magento'],
    'data': ['views/product.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
