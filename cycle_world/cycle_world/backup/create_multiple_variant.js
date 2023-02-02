show_multiple_variants_dialog: function(frm) {
    var me = this;

    let promises = [];
    let attr_val_fields = {};

    function make_fields_from_attribute_values(attr_dict) {
        let fields = [];
        Object.keys(attr_dict).forEach((name, i) => {
            if(i % 4 === 0){
                fields.push({fieldtype: 'Section Break'});
            }
            fields.push({fieldtype: 'Column Break', label: name});
            attr_dict[name].forEach(value => {
                fields.push({
                    fieldtype: 'Check',
                    label: value,
                    fieldname: value,
                    default: 0,
                    onchange: function() {
                        let selected_attributes = get_selected_attributes();
                        let lengths = [];
                        Object.keys(selected_attributes).map(key => {
                            lengths.push(selected_attributes[key].length);
                        });
                        if(lengths.includes(0)) {
                            me.multiple_variant_dialog.get_primary_btn().html(__('Create Variants'));
                            // me.multiple_variant_dialog.disable_primary_action();
                        } else {

                            let no_of_combinations = lengths.reduce((a, b) => a * b, 1);
                            let msg;
                            if (no_of_combinations === 1) {
                                msg = __("Make {0} Variant", [no_of_combinations]);
                            } else {
                                msg = __("Make {0} Variants", [no_of_combinations]);
                            }
                            me.multiple_variant_dialog.get_primary_btn().html(msg);
                            me.multiple_variant_dialog.enable_primary_action();
                        }
                    }
                });
            });
        });
        return fields;
    }

    function make_and_show_dialog(fields, attr_dict) {
        me.multiple_variant_dialog = new frappe.ui.Dialog({
            title: __("Select Attribute Values"),
            size:'large',
            fields: [
                {
                    fieldtype: "HTML",
                    fieldname: "help",
                    options: `<label class="control-label">
                        ${__("Select at least one value from each of the attributes.")}
                    </label>`,
                }
            ].concat(fields)
        });

        me.multiple_variant_dialog.set_primary_action(__('Create Variants'), () => {
            let selected_attributes = get_selected_attributes();

            me.multiple_variant_dialog.hide();
            frappe.call({
                method: "erpnext.controllers.item_variant.enqueue_multiple_variant_creation",
                args: {
                    "item": frm.doc.name,
                    "args": selected_attributes
                },
                callback: function(r) {
                    if (r.message==='queued') {
                        frappe.show_alert({
                            message: __("Variant creation has been queued."),
                            indicator: 'orange'
                        });
                    } else {
                        frappe.show_alert({
                            message: __("{0} variants created.", [r.message]),
                            indicator: 'green'
                        });
                    }
                }
            });
        });

        $($(me.multiple_variant_dialog.$wrapper.find('.form-column'))
            .find('.frappe-control')).css('margin-bottom', '0px');
        let attr_id = {};
        Array.from($(me.multiple_variant_dialog.$wrapper.find('.form-column'))).forEach((ele)=>{
            if(ele.innerText.indexOf('Select at least one value from each of the attributes.')<=-1)
            {
                var search = `
                <div class="dropdown-search">
                    <input type="text"
                        placeholder="Search ${$(ele).find('.control-label')[0].innerText}"
                        data-element="search"
                        data-attribute="${$(ele).find('.control-label')[0].innerText}"
                        class="dropdown-search-input form-control input-xs"
                        id="${$(ele).find('.control-label')[0].innerText}-search"
                    >
                </div>
                `;
                var search_div = document.createElement('div');
                search_div.classList.add($(ele).find('.control-label')[0].innerText.trim().split(' ').join('_'))
                search_div.innerHTML=search;
                ele.prepend(search_div)
                
                attr_id[$(ele).find('.control-label')[0].innerText] = $(ele).find('.control-label')[0].innerText.split(' ').join('_').toLowerCase()
                var create_html = `
                <button id="${attr_id[$(ele).find('.control-label')[0].innerText]}" class = 'btn btn-sm btn-modal-primary' type='button' 
                    style='background-color:#98dff5;color:black;width:60px;height:25px;margin-top:5px;text-align:center;padding-top: 3px;'>
                    Create
                </div>
                `
                var create_button = document.createElement('div');
                create_button.innerHTML = create_html;
                create_button.style.float='right'
                var label = ele.getElementsByClassName('control-label')[0];
                label.parentNode.insertBefore(create_button, label.nextSibling);
                create_button.addEventListener('click', ()=>{
                    var doc = frappe.model.get_new_doc('CW Item Attribute');
                    doc.item_attribute = $(ele).find('.control-label')[0].innerText;
                    doc.attribute_value = (me.multiple_variant_dialog.wrapper[0].querySelector(`[id="${$(ele).find('.control-label')[0].innerText}-search"]`).value || "").toLowerCase().split(' ').join('');
                    doc.abbr = '';
                    frappe.ui.form.make_quick_entry('CW Item Attribute', function(doc){
                        var new_field = document.createElement('div')
                        new_field.classList.add('form-group')
                        new_field.classList.add('frappe-control')
                        new_field.classList.add('input-max-width')
                        new_field.setAttribute('data-fieldname', doc.attribute_value)
                        new_field.setAttribute('data-fieldtype', 'Check')
                        new_field.setAttribute('title', doc.attribute_value)
                        var search_value = (me.multiple_variant_dialog.wrapper[0].querySelector(`[id="${doc.item_attribute}-search"]`).value || "").toLowerCase().split(' ').join('')
                        var visibility='';
                        if(doc.attribute_value.toLowerCase().split(' ').join('').indexOf(search_value)<0){
                            visibility='hidden';
                        }
                        new_field.innerHTML=`
                        <div class="form-group frappe-control input-max-width" data-fieldtype="Check" data-fieldname="${doc.attribute_value}" title="${doc.attribute_value}" style="margin-bottom: 0px;">
                        <div class='checkbox ${visibility}'>
                        <label>
                            <span class="input-area" style="display: inline;">
                                <input type="checkbox" autocomplete="off" class="input-with-feedback" data-fieldtype="Check" data-fieldname="${doc.attribute_value}" placeholder="">
                            </span>
                            <span class="disp-area" style="display: none;"><input type="checkbox" disabled="" class="disabled-deselected"></span>
                            <span class="label-area">${doc.attribute_value}</span>
                        </label>
                        <p class="help-box small text-muted"></p>
                        </div>
                        `
                        attr_dict[doc.item_attribute].push(doc.attribute_value)
                        ele.append(new_field)
                        document.querySelectorAll(`input[data-fieldname="${doc.attribute_value}"]`)[0].focus();
                    }, undefined, doc)
                })
            }
        })
        // me.multiple_variant_dialog.disable_primary_action();
        me.multiple_variant_dialog.clear();
        me.multiple_variant_dialog.show();
        setTimeout(() => {
        Object.keys(attr_dict).forEach((attr)=>{
            var search_node = document.getElementsByClassName(attr.trim().split(' ').join('_'))
            search_node.item(search_node.length-1).addEventListener('input', function(){
                var search_value = (me.multiple_variant_dialog.wrapper[0].querySelector(`[id="${attr}-search"]`).value || "").toLowerCase().split(' ').join('')
                var temp = document.getElementsByClassName(attr.split(' ').join('_'));
                var parent = temp.item(temp.length - 1).parentElement
                attr_dict[attr].forEach((val)=>{
                    var ele = parent.querySelectorAll(`input[data-fieldname *="${val?.trim() || ''}"]`)
                    ele.forEach((node)=>{
                        var check_box = node.parentElement.parentElement.parentElement;
                    if(val.toLowerCase().split(' ').join('').indexOf(search_value)>=0){
                        
                        if(check_box.classList.contains('hidden')){
                            check_box.classList.remove('hidden')
                        }
                    }
                    else{
                        if(!check_box.classList.contains('hidden') && node.getAttribute('data-fieldname').toLowerCase().split(' ').join('').indexOf(search_value)<0){
                            check_box.classList.add('hidden')
                        }
                    }
                    })
                    

                })
            })
        })
    }, 1000);
         
    }

    function get_selected_attributes() {
        let selected_attributes = {};
        me.multiple_variant_dialog.$wrapper.find('.form-column').each((i, col) => {
            if(i===0) return;
            let attribute_name = $(col).find('label').html().trim();
            selected_attributes[attribute_name] = [];
            let checked_opts = $(col).find('.checkbox input');
            checked_opts.each((i, opt) => {
                if($(opt).is(':checked')) {
                    selected_attributes[attribute_name].push($(opt).attr('data-fieldname'));
                }
            });
        });

        return selected_attributes;
    }

    frm.doc.attributes.forEach(function(d) {
        let p = new Promise(resolve => {
            if(!d.numeric_values) {
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Item Attribute Value",
                        filters: [
                            ["parent","=", d.attribute]
                        ],
                        fields: ["attribute_value"],
                        limit_page_length: 0,
                        parent: "Item Attribute",
                        order_by: "attribute_value"
                    }
                }).then((r) => {
                    if(r.message) {
                        attr_val_fields[d.attribute] = r.message.map(function(d) { return d.attribute_value; });
                        resolve();
                    }
                });
            } else {
                frappe.call({
                    method: "frappe.client.get",
                    args: {
                        doctype: "Item Attribute",
                        name: d.attribute,
                        order_by: 'name'
                    }
                }).then((r) => {
                    if(r.message) {
                        const from = r.message.from_range;
                        const to = r.message.to_range;
                        const increment = r.message.increment;

                        let values = [];
                        for(var i = from; i <= to; i = flt(i + increment, 6)) {
                            values.push(i);
                        }
                        attr_val_fields[d.attribute] = values;
                        resolve();
                    }
                });
            }
        });

        promises.push(p);

    }, this);

    Promise.all(promises).then(() => {
        let fields = make_fields_from_attribute_values(attr_val_fields);
        make_and_show_dialog(fields, attr_val_fields);
    })

},