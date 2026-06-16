var web_id = 1;

var buttons_clicked = 0;
var vis = [];
var feature_values = [];
var csv_downloaded = false;

var screen_width = window.innerWidth;
var screen_height = window.innerHeight;

var total_number_of_buttons_in_the_website = 0;
var total_number_of_buttons_in_the_navbar = 0;

var largest_text_size = 0;
var smallest_text_size = Number.MAX_SAFE_INTEGER;

var largest_button_width = 0;
var smallest_button_width = Number.MAX_SAFE_INTEGER;

var largest_button_height = 0;
var smallest_button_height = Number.MAX_SAFE_INTEGER;

var extractRGB = function(colorString) {
    //console.log(colorString);
    if (colorString.startsWith('rgb')) {
        
        var rgbaValues = colorString.substring(colorString.indexOf('(') + 1, colorString.lastIndexOf(')')).split(',');
        
        var red = parseInt(rgbaValues[0]);
        var green = parseInt(rgbaValues[1]);
        var blue = parseInt(rgbaValues[2]);
        
        var alpha = 1;
        if (colorString.startsWith('rgba')) {
            alpha = parseFloat(rgbaValues[3]);
        }
        //console.log("yuck");
        return { red: red, green: green, blue: blue, alpha: alpha };
    }
    // If the color string is not in 'rgb' or 'rgba' format, return rgb( 0, 0, 0) as default
    return { red: 0, green: 0, blue: 0 , alpha: 1 };
}

function getRelativeLuminance(rgbColors) {
    var r = parseInt(rgbColors.red) / 255;
    var g = parseInt(rgbColors.green) / 255;
    var b = parseInt(rgbColors.blue) / 255;

    // Calculate relative luminance
    var luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    return luminance;
}

function calculateContrast(rgbColor1, rgbColor2) {
    // Get relative luminance of each color
    var luminance1 = getRelativeLuminance(rgbColor1);
    var luminance2 = getRelativeLuminance(rgbColor2);

    // Calculate contrast ratio
    var contrastRatio = (Math.max(luminance1, luminance2) + 0.05) / (Math.min(luminance1, luminance2) + 0.05);
    return contrastRatio;
}

var is_in_navbar = function(button) {
    ret = false;
    par = button.parentNode;
    while(true) {
        if(par === document.body) {
            break;
        }
        if(par.tagName === 'NAV') {
            ret = true;
            break;
        }
        par = par.parentNode;
    }
    return ret;
}

var is_in_footer = function(button) {
    ret = false;
    par = button.parentNode;
    while(true) {
        if(par === document.body) {
            break;
        }
        if(par.tagName === 'FOOTER') {
            ret = true;
            break;
        }
        par = par.parentNode;
    }
    return ret;
}

var get_web_properties = function() {
    var buttons = document.querySelectorAll("button,a");
    buttons.forEach(function(button) {
        var computedStyles_loop = window.getComputedStyle(button);

        var text_size_loop = parseInt(computedStyles_loop.getPropertyValue("font-size"));
        largest_text_size = Math.max(largest_text_size, text_size_loop);
        smallest_text_size = Math.min(smallest_text_size, text_size_loop);
    
        var button_width_loop = parseInt(computedStyles_loop.getPropertyValue("width"));
        largest_button_width = Math.max(largest_button_width, button_width_loop);
        smallest_button_width = Math.min(smallest_button_width, button_width_loop);

        var button_height_loop = parseInt(computedStyles_loop.getPropertyValue("height"));
        largest_button_height = Math.max(largest_button_height, button_height_loop);
        smallest_button_height = Math.min(smallest_button_height, button_height_loop);

        var rect_loop = button.getBoundingClientRect();
        var x_loop = (rect_loop.left + rect_loop.right) / 2;
        var y_loop = (rect_loop.top + rect_loop.bottom) / 2;

        if(is_in_navbar(button)) {
            total_number_of_buttons_in_the_navbar += 1;
        }

        if(x_loop <= screen_width && y_loop <= screen_height) {
            total_number_of_buttons_in_the_website += 1;
        }

        //console.log("done")

    });
}

var get_features = function(clicked_this) {
    
    // PREPROCESSING

    var total_number_of_buttons_in_radius_5_percent_of_screen_size = 0;
    var total_number_of_buttons_in_radius_10_percent_of_screen_size = 0;
    var total_number_of_buttons_in_radius_25_percent_of_screen_size = 0;
    var total_number_of_buttons_in_radius_50_percent_of_screen_size = 0;

    var rect = clicked_this.getBoundingClientRect();
    var x = (rect.left + rect.right) / 2;
    var y = (rect.top + rect.bottom) / 2;
    
    var buttons = document.querySelectorAll("button,a");
    var button_id = -1;
    var i = 1;
    buttons.forEach(function(button) {

        var rect_loop = button.getBoundingClientRect();
        var x_loop = (rect_loop.left + rect_loop.right) / 2;
        var y_loop = (rect_loop.top + rect_loop.bottom) / 2;
        var dist_x = Math.abs(x-x_loop);
        var dist_y = Math.abs(y-y_loop);

        //console.log(button.textContent, " dist: ", dist_x, dist_y);

        if(dist_x != 0 || dist_y !=0) {
            if(dist_x <= screen_width * 0.05 && dist_y <= screen_height * 0.05) {
                total_number_of_buttons_in_radius_5_percent_of_screen_size += 1;
            }
            if(dist_x <= screen_width * 0.1 && dist_y <= screen_height * 0.1) {
                total_number_of_buttons_in_radius_10_percent_of_screen_size += 1;
            }
            if(dist_x <= screen_width * 0.25 && dist_y <= screen_height * 0.25) {
                total_number_of_buttons_in_radius_25_percent_of_screen_size += 1;
            }
            if(dist_x <= screen_width * 0.5 && dist_y <= screen_height * 0.5) {
                total_number_of_buttons_in_radius_50_percent_of_screen_size += 1;
            }
        }
        else {
            button_id = i;
        }

        if(x_loop <= screen_width && y_loop <= screen_height) {
            i += 1;
        }

    });
    
    var computedStyles = window.getComputedStyle(clicked_this);


    // BUTTON APPEARANCE
    
    var button_width = parseInt(computedStyles.getPropertyValue("width"));
    var button_width_ratio_with_largest_button_width = button_width / largest_button_width;
    var button_width_ratio_with_smallest_button_width = button_width / smallest_button_width;

    var button_height = parseInt(computedStyles.getPropertyValue("height"));
    var button_height_ratio_with_largest_button_height = button_height / largest_button_height;
    var button_height_ratio_with_smallest_button_height = button_height / smallest_button_height;

    var button_colors = extractRGB(computedStyles.getPropertyValue("background-color"));
    //console.log("button_colors");
    //console.log(button_colors);
    var button_color_R = button_colors.red;
    var button_color_G = button_colors.green;
    var button_color_B = button_colors.blue;
    var button_color_A = button_colors.alpha;

    var computedStyles_parent = window.getComputedStyle(clicked_this.parentNode);

    var parent_colors = extractRGB(computedStyles_parent.getPropertyValue("background-color"));
    //console.log("parent_colors");
    //console.log(parent_colors);
    var button_contrast_with_background = calculateContrast(button_colors,parent_colors);


    // BUTTON PLACEMENT

    var button_center_x_coordinate = x;
    var button_center_y_coordinate = y;
    var button_is_on_navbar = is_in_navbar(clicked_this);
    var button_is_on_footer = is_in_footer(clicked_this);
    var button_is_on_left_half_of_screen = button_center_x_coordinate < (screen_width / 2);
    var button_is_on_right_half_of_screen = button_center_x_coordinate > (screen_width / 2);
    var button_is_on_upper_half_of_screen = button_center_y_coordinate < (screen_height / 2);
    var button_is_on_lower_half_of_screen = button_center_y_coordinate > (screen_height / 2);
    var button_is_on_horizontal_center_of_screen = button_center_x_coordinate == (screen_width / 2);
    var button_is_on_vertical_center_of_screen = button_center_y_coordinate == (screen_height / 2);


    // BUTTON SURROUNDINGS

    total_number_of_buttons_in_radius_5_percent_of_screen_size = total_number_of_buttons_in_radius_5_percent_of_screen_size;
    total_number_of_buttons_in_radius_10_percent_of_screen_size = total_number_of_buttons_in_radius_10_percent_of_screen_size;
    total_number_of_buttons_in_radius_25_percent_of_screen_size = total_number_of_buttons_in_radius_25_percent_of_screen_size;
    total_number_of_buttons_in_radius_50_percent_of_screen_size = total_number_of_buttons_in_radius_50_percent_of_screen_size;


    // BUTTON TEXT

    var button_text_size = parseInt(computedStyles.getPropertyValue("font-size"));
    var button_text_size_ratio_with_largest_button_text = button_text_size / largest_text_size;
    var button_text_size_ratio_with_smallest_button_text = button_text_size / smallest_text_size;

    var text_colors = extractRGB(computedStyles.getPropertyValue("color"));
    //console.log("text_colors");
    //console.log(text_colors);
    var button_text_color_R = text_colors.red;
    var button_text_color_G = text_colors.green;
    var button_text_color_B = text_colors.blue;
    var button_text_color_A = text_colors.alpha;
    var button_text_contrast_with_button = calculateContrast(text_colors,button_colors);

    var button_text_is_bold = computedStyles.getPropertyValue("font-weight") >= "600";
    var button_text_is_italic = computedStyles.getPropertyValue("font-style") === "italic";


    // WEBSITE'S PROPERTIES

    total_number_of_buttons_in_the_website = total_number_of_buttons_in_the_website;
    total_number_of_buttons_in_the_navbar = total_number_of_buttons_in_the_navbar;
    largest_button_text_in_the_website = largest_text_size;
    smallest_button_text_in_the_website = smallest_text_size;
    largest_button_width_in_the_website = largest_button_width;
    smallest_button_width_in_the_website = smallest_button_width;
    largest_button_height_in_the_website = largest_button_height;
    smallest_button_height_in_the_website = smallest_button_height;
    

    return {
        web_id: web_id,
        button_id: button_id,
        
        // button_appearance
        button_width: button_width / screen_width,
        button_width_ratio_with_largest_button_width: button_width_ratio_with_largest_button_width,
        button_width_ratio_with_smallest_button_width: button_width_ratio_with_smallest_button_width,
        button_height: button_height / screen_height,
        button_height_ratio_with_largest_button_height: button_height_ratio_with_largest_button_height,
        button_height_ratio_with_smallest_button_height: button_height_ratio_with_smallest_button_height,
        button_color_R: button_color_R / 255,
        button_color_G: button_color_G / 255,
        button_color_B: button_color_B / 255,
        button_color_A: button_color_A,
        button_contrast_with_background: button_contrast_with_background / 21,
        
        // button_placement
        button_center_x_coordinate: button_center_x_coordinate / screen_width,
        button_center_y_coordinate: button_center_y_coordinate / screen_height,
        button_is_on_navbar: button_is_on_navbar?1:0,
        button_is_on_footer: button_is_on_footer?1:0,
        button_is_on_left_half_of_screen: button_is_on_left_half_of_screen?1:0,
        button_is_on_right_half_of_screen: button_is_on_right_half_of_screen?1:0,
        button_is_on_upper_half_of_screen: button_is_on_upper_half_of_screen?1:0,
        button_is_on_lower_half_of_screen: button_is_on_lower_half_of_screen?1:0,
        button_is_on_horizontal_center_of_screen: button_is_on_horizontal_center_of_screen?1:0,
        button_is_on_vertical_center_of_screen: button_is_on_vertical_center_of_screen?1:0,
        
        // button_surroundings
        total_number_of_buttons_in_radius_5_percent_of_screen_size: total_number_of_buttons_in_radius_5_percent_of_screen_size / (total_number_of_buttons_in_the_website-1),
        total_number_of_buttons_in_radius_10_percent_of_screen_size: total_number_of_buttons_in_radius_10_percent_of_screen_size / (total_number_of_buttons_in_the_website-1),
        total_number_of_buttons_in_radius_25_percent_of_screen_size: total_number_of_buttons_in_radius_25_percent_of_screen_size / (total_number_of_buttons_in_the_website-1),
        total_number_of_buttons_in_radius_50_percent_of_screen_size: total_number_of_buttons_in_radius_50_percent_of_screen_size / (total_number_of_buttons_in_the_website-1),
        
        // button_text
        button_text_size: button_text_size,
        button_text_size_ratio_with_largest_button_text: button_text_size_ratio_with_largest_button_text,
        button_text_size_ratio_with_smallest_button_text: button_text_size_ratio_with_smallest_button_text,
        button_text_color_R: button_text_color_R / 255,
        button_text_color_G: button_text_color_G / 255,
        button_text_color_B: button_text_color_B / 255,
        button_text_color_A: button_text_color_A,
        button_text_contrast_with_button: button_text_contrast_with_button / 21,
        button_text_is_bold: button_text_is_bold?1:0,
        button_text_is_italic: button_text_is_italic?1:0,
        
        // website_properties
        total_number_of_buttons_in_the_website: total_number_of_buttons_in_the_website,
        total_number_of_buttons_in_the_navbar: total_number_of_buttons_in_the_navbar / total_number_of_buttons_in_the_website,
        largest_button_text_in_the_website: largest_button_text_in_the_website,
        smallest_button_text_in_the_website: smallest_button_text_in_the_website,
        largest_button_width_in_the_website: largest_button_width_in_the_website,
        smallest_button_width_in_the_website: smallest_button_width_in_the_website,
        largest_button_height_in_the_website: largest_button_height_in_the_website,
        smallest_button_height_in_the_website: smallest_button_height_in_the_website,
        
        // target
        button_rank: 0
    };
    
}

function objectsToCSV(objects) {
    var keys = Object.keys(objects[0]);

    objects.sort(function(a, b) {
        var columnA = a[keys[1]];
        var columnB = b[keys[1]];
        return columnA - columnB;
    });

    var rows = objects.map(obj => keys.map(key => obj[key]));
    var csvContent = '';
    csvContent += keys.join(',') + '\n';
    csvContent += rows.map(row => row.join(',')).join('\n');

    return csvContent;
}

function downloadCSV(filename, csvContent) {
    var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

    var link = document.createElement("a");
    if (link.download !== undefined) {
        link.setAttribute("href", URL.createObjectURL(blob));
        link.setAttribute("download", filename);

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        console.log("Your browser does not support the download attribute.");
    }
}

var test_func = function(button) {
    features = get_features(button);

    //console.log("---------------------------------")

    //console.log(features.button_id);

    if(!vis[features.button_id]) {
        vis[features.button_id] = true;
        buttons_clicked += 1;
        features.button_rank = (total_number_of_buttons_in_the_website - buttons_clicked) / (total_number_of_buttons_in_the_website - 1);
        //feature_values[features.button_id] = features;
        feature_values.push(features);
    }

    if(buttons_clicked == total_number_of_buttons_in_the_website) {
        if(!csv_downloaded) {
            csv_downloaded = true;
            downloadCSV("test_data.csv",objectsToCSV(feature_values));
        }
        //console.log(feature_values);
    }

    //console.log(buttons_clicked);
    //console.log(total_number_of_buttons_in_the_website);

}

var stop_timer = function(test_timer) {
    clearTimeout(test_timer);
}

var testtest = function() {
    var buttons = document.querySelectorAll("button,a");
    var counter = 0;
    buttons.forEach(function(button) {
        
        console.log(button);
        counter = counter + 1;
        console.log(counter);

    });
}

window.addEventListener('DOMContentLoaded', event => {
    //testtest();
    get_web_properties();
    //console.log('hello world ',buttons_clicked)
    
    var test_timeout = function() {
        console.log('bye world ',buttons_clicked)
        // Example usage:
        var filename = "example.csv";
        var csvContent = "Column1,Column2,Column3\nValue1,Value2,Value3\nValue4,Value5,Value6";
        //downloadCSV(filename, csvContent);
    }
    
    //test_timer = setTimeout(test_timeout,7000);
    
});