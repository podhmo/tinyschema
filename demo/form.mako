<%def name="render_field(field)">
  ${getattr(self, field.widget)(field)}
</%def>

<%def name="select(field)">
  <select>
     %for v, name in field.choices:
       %if field.value == v:
         <option value="${v}" selected="selected">${name}</option>
       %else:
         <option value="${v}">${name}</option>
       %endif
     %endfor
  </select>
</%def>
