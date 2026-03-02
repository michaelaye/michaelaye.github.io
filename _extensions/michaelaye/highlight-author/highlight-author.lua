-- highlight-author.lua
-- Pandoc/Quarto filter that highlights a specified author name in bibliography
-- entries. Supports bold, italic, underline, and custom CSS class styles.
--
-- Requires: citeproc: false in YAML (so this filter controls when citeproc runs).
--
-- Usage in YAML front matter:
--   highlight-author:
--     name: "Aye"          # surname to match
--     style: bold          # bold | italic | underline | <css-class-name>
--
-- Or shorthand (defaults to bold):
--   highlight-author: "Aye"

--- Check if a Str element's text looks like a name part (initial or given name).
-- Matches: K, K., K-M, K.-M., Klaus, Michael, Klaus-Michael, -M., etc.
-- Does NOT match: and, et, al., 2020, lowercase words
local function is_name_part(text)
  return text:match("^%-?%u") ~= nil
end

--- Wrap inlines in the appropriate highlight element based on style.
local function wrap_highlight(inlines, style)
  if style == "bold" then
    return pandoc.Strong(inlines)
  elseif style == "italic" then
    return pandoc.Emph(inlines)
  elseif style == "underline" then
    return pandoc.Underline(inlines)
  else
    -- Treat as CSS class name
    return pandoc.Span(inlines, pandoc.Attr("", {style}))
  end
end

--- Process an Inlines list to wrap all occurrences of the target surname
--- and surrounding name parts in the chosen highlight element.
local function highlight_author_name(inlines, surname, style)
  local pattern = "^" .. surname .. "[,.]?$"

  local items = {}
  for _, el in ipairs(inlines) do
    items[#items + 1] = el
  end

  local result = pandoc.Inlines{}
  local i = 1

  while i <= #items do
    local el = items[i]

    if el.t == "Str" and el.text:match(pattern) then
      local name_text = el.text
      local clean_name = name_text:gsub("[,.]$", "")
      local trailing = name_text:sub(#clean_name + 1)

      -- Determine if surname-first ("Aye, Klaus Michael") or
      -- given-name-first ("Klaus-Michael Aye")
      local prev_is_name = false
      if #result >= 2 then
        local prev1 = result[#result]
        local prev2 = result[#result - 1]
        if prev1.t == "Space" and prev2.t == "Str"
           and is_name_part(prev2.text) and not prev2.text:match(",$") then
          prev_is_name = true
        end
      end

      if not prev_is_name and trailing == "," then
        ---------------------------------------------------------
        -- SURNAME-FIRST: "Aye, K M, ..." or "Aye, Klaus Michael, ..."
        ---------------------------------------------------------
        local group = pandoc.Inlines{pandoc.Str(name_text)}
        local j = i + 1
        local done = false

        while j + 1 <= #items and not done do
          if items[j].t == "Space" and items[j + 1].t == "Str" then
            local txt = items[j + 1].text
            if is_name_part(txt) then
              local clean = txt:gsub("[,.]$", "")
              local trail = txt:sub(#clean + 1)
              group:insert(pandoc.Space())
              if trail ~= "" then
                group:insert(pandoc.Str(clean))
                result:insert(wrap_highlight(group, style))
                result:insert(pandoc.Str(trail))
                j = j + 2
                done = true
              else
                group:insert(pandoc.Str(txt))
                j = j + 2
              end
            else
              break
            end
          else
            break
          end
        end

        if not done then
          result:insert(wrap_highlight(group, style))
        end
        i = j

      elseif prev_is_name then
        ---------------------------------------------------------
        -- GIVEN-NAME-FIRST: "K-M Aye," or "Klaus-Michael Aye"
        ---------------------------------------------------------
        local back_elems = pandoc.List{}
        while #result > 0 do
          local last = result[#result]
          if last.t == "Space" then
            back_elems:insert(1, table.remove(result, #result))
          elseif last.t == "Str" then
            if last.text:match(",$") then
              break
            elseif is_name_part(last.text) then
              back_elems:insert(1, table.remove(result, #result))
            else
              break
            end
          else
            break
          end
        end
        while #back_elems > 0 and back_elems[1].t == "Space" do
          result:insert(back_elems:remove(1))
        end
        back_elems:insert(pandoc.Str(clean_name))
        result:insert(wrap_highlight(pandoc.Inlines(back_elems), style))
        if trailing ~= "" then
          result:insert(pandoc.Str(trailing))
        end
        i = i + 1

      else
        -- Standalone surname without clear name context
        result:insert(wrap_highlight({pandoc.Str(clean_name)}, style))
        if trailing ~= "" then
          result:insert(pandoc.Str(trailing))
        end
        i = i + 1
      end
    else
      result:insert(el)
      i = i + 1
    end
  end

  return result
end

function Pandoc(doc)
  -- Read configuration from metadata
  local meta = doc.meta["highlight-author"]
  if not meta then
    return doc
  end

  local surname, style

  local meta_type = pandoc.utils.type(meta)

  if meta_type == "Inlines" then
    -- Shorthand: highlight-author: "Aye"
    surname = pandoc.utils.stringify(meta)
    style = "bold"
  elseif meta_type == "table" then
    surname = meta.name and pandoc.utils.stringify(meta.name) or nil
    style = meta.style and pandoc.utils.stringify(meta.style) or "bold"
  else
    io.stderr:write("highlight-author: invalid configuration (type: " .. meta_type .. ")\n")
    return doc
  end

  if not surname or surname == "" then
    io.stderr:write("highlight-author: no author name specified\n")
    return doc
  end

  -- Run citeproc to generate the bibliography
  doc = pandoc.utils.citeproc(doc)

  -- Walk the refs div and highlight the author name
  doc.blocks = doc.blocks:walk({
    Div = function(div)
      if div.identifier ~= "refs" then
        return nil
      end

      for _, elem in ipairs(div.content) do
        if elem.t == "Div" then
          for bi, block in ipairs(elem.content) do
            if (block.t == "Para" or block.t == "Plain") and block.content then
              elem.content[bi] = pandoc[block.t](
                highlight_author_name(block.content, surname, style)
              )
            end
          end
        end
      end

      return div
    end
  })

  return doc
end
