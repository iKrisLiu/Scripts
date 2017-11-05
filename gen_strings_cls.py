import os
import re
import sys
import datetime
import plistlib
import ConfigParser
from string import Template

input_dir_path = os.path.normpath(sys.argv[1])
output_dir_path = os.path.normpath(sys.argv[2])

header_template_string_format = '''/**
 * DO NOT CHANGE THIS FILE MANULLY!!!
 * Generated on: %s
 */

@import ZZFoundation;

NS_ASSUME_NONNULL_BEGIN

@interface ZZLocalizableStrings (%s)

${PROPERTY_DECLARATION}
@end

NS_ASSUME_NONNULL_END'''

impl_template_string_format = '''/**
 * DO NOT CHANGE THIS FILE MANULLY!!!
 * Generated on: %s
 */

#import "%s"

@interface %sBundle : NSObject @end
@implementation %sBundle @end


@implementation ZZLocalizableStrings (%s)

${PROPERTY_IMPLEMENTATION}
@end'''

def generate_strings(strings_file, stringsdict_file):
# define local variables
    strings_path = os.path.join(input_dir_path, strings_file)
    stringsdict_path = os.path.join(input_dir_path, stringsdict_file)

    string_table_name = os.path.splitext(strings_file)[0]
    class_category_name = string_table_name.replace(' ', '')

    output_header_file_path = '{}/R+{}.h'.format(output_dir_path, class_category_name)
    output_impl_file_path = '{}/R+{}.m'.format(output_dir_path, class_category_name)
    output_header_file_name = os.path.basename(output_header_file_path)

# define templates
    header_template = header_template_string_format % (datetime.datetime.now(), class_category_name)
    implementation_template = impl_template_string_format % (datetime.datetime.now(), output_header_file_name, class_category_name, class_category_name, class_category_name)
    property_declaration_template = '''@property (nonatomic, readonly) NSString *${PROPERTY_NAME};  ///< ${COMMENT}'''
    property_implementation_template = '''- (NSString *)${PROPERTY_NAME} { return ZZLocalizedStringFromTableInBundle(@"${STRING_KEY}", @"%s", [NSBundle bundleForClass:%sBundle.self]); }''' % (string_table_name, class_category_name)

# parse strings
    string_property_dict = {}
    if os.path.isfile(strings_path):
        input_strings = open(strings_path, 'r')
        input_strings_temp_name = strings_path + '.temp'
        input_strings_temp = open(input_strings_temp_name, 'w')

        # Convert .strings file to .ini format
        config_parser_title = 'Strings'
        input_strings_temp.write('[%s]\n' % config_parser_title)

        # remove comments
        rule1 = "(\/\*(\s|.)*?\*\/)|(\/\/.*)"
        lines = input_strings.read()
        input_strings.close()
        lines = re.sub(rule1, '', lines)

        # delete space in each begin of line
        rule2 = "(^\s+)"
        lines = re.sub(rule2, '', lines)

        # save it in a temp file
        input_strings_temp.write(lines)
        input_strings_temp.close()

        config_parser = ConfigParser.ConfigParser()
        # preserve case
        config_parser.optionxform = str
        config_parser.read(input_strings_temp_name)
        string_pair = config_parser.items(config_parser_title)

        for pair in string_pair:
            string_key = pair[0][1:-1]
            string_value = pair[1][1:-2]
            if string_key:
                string_property_dict[string_key] = string_value

        os.remove(input_strings_temp_name)

# parse strings dict
    if os.path.isfile(stringsdict_path):
        dictionary = plistlib.readPlist(stringsdict_path)
        for string_key in dictionary:
            try:
                string_value = dictionary[string_key]["custom_key"]["other"]
            except KeyError as e:
                string_value = ""
            string_property_dict[string_key] = string_value     # Used as comment

# generate R file
    property_declarations = ''
    property_implementations = ''
    for string_key, string_value in string_property_dict.items():
        property_declaration = Template(property_declaration_template).substitute(PROPERTY_NAME=string_key, COMMENT=string_value)
        property_declarations += property_declaration + '\n'
        property_implementation = Template(property_implementation_template).substitute(PROPERTY_NAME=string_key, STRING_KEY=string_key)
        property_implementations += property_implementation + '\n'

    new_header_content = Template(header_template).substitute(PROPERTY_DECLARATION=property_declarations)
    new_impl_content = Template(implementation_template).substitute(PROPERTY_IMPLEMENTATION=property_implementations)

    # overwrite R.h if necessary
    header_file = open(output_header_file_path, 'w+')
    if header_file.read() != new_header_content:
        header_file.write(new_header_content)
    header_file.close()

    # overwrite R.m if necessary
    implementation_file = open(output_impl_file_path, 'w+')
    if implementation_file.read() != new_impl_content:
        implementation_file.write(new_impl_content)
    implementation_file.close()


def main():
    if not os.path.isdir(input_dir_path):
        print 'Input directory is not a directory'
    elif not os.path.isdir(output_dir_path):
        print 'Output directory is not a directory'
    else:
        file_names = []
        for file_name in os.listdir(input_dir_path):
            if file_name.lower().endswith('strings') or file_name.lower().endswith('stringsdict'):
                file_names.append(os.path.splitext(file_name)[0])

        for file_name in list(set(file_names)):
            generate_strings(file_name + '.strings', file_name + '.stringsdict')

if __name__ == '__main__':
    main()