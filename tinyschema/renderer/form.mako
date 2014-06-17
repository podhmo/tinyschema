<%def name="render_field(field)">
  ${getattr(self, field.widget)(field)}
</%def>

<%def name="options(kwargs)">
%for k, vs in kwargs.items():
 "${k}"="${vs}"\
%endfor
</%def>\

<%def name="select(field)">
<select name="${field.name}">
   %for v, name in field.choices:
     %if field.value == v:
<option value="${v}" selected="selected">${name}</option>
     %else:
<option value="${v}">${name}</option>
     %endif
   %endfor
</select>
</%def>

<%def name="checkbox(field)">
  %for v, label in field.choices:
    %if field.value == v:
<label>${label}<input type="checkbox" checked="checked" name="${field.name}" value="${v}"></input></label>
    %else:
<label>${label}<input type="checkbox" name="${field.name}" value="${v}"></input></label>
    %endif
  %endfor
</%def>

<%def name="radio(field)">
  %for v, label in field.choices:
    %if field.value == v:
<label>${label}<input type="radio" checked="checked" name="${field.name}" value="${v}"></input></label>
    %else:
<label>${label}<input type="radio" name="${field.name}" value="${v}"></input></label>
    %endif
  %endfor
</%def>
