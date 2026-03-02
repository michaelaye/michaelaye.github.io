-- group-by-year.lua
-- Pandoc Lua filter that runs citeproc, then:
--   1. Bolds all variations of the author's name in each entry
--   2. Groups bibliography entries by year with reverse-chronological headings
-- Requires: citeproc: false in YAML (so we control when citeproc runs).

--- Check if a Str element's text looks like a name part (initial or given name).
-- Matches: K, K., K-M, K.-M., Klaus, Michael, Klaus-Michael, -M., etc.
-- Does NOT match: and, et, al., 2020, lowercase words
local function is_name_part(text)
  return text:match("^%-?%u") ~= nil
end

--- Process an Inlines list to wrap all occurrences of "Aye" + surrounding
--- name parts in pandoc.Strong.
local function bold_aye_name(inlines)
  local items = {}
  for _, el in ipairs(inlines) do
    items[#items + 1] = el
  end

  local result = pandoc.Inlines{}
  local i = 1

  while i <= #items do
    local el = items[i]

    if el.t == "Str" and el.text:match("^Aye[,.]?$") then
      local aye_text = el.text
      local clean_aye = aye_text:gsub("[,.]$", "")
      local trailing = aye_text:sub(#clean_aye + 1)

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
        local group = pandoc.Inlines{pandoc.Str(aye_text)}
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
                -- Trailing comma/period marks end of given name
                group:insert(pandoc.Str(clean))
                result:insert(pandoc.Strong(group))
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
          result:insert(pandoc.Strong(group))
        end
        i = j

      elseif prev_is_name then
        ---------------------------------------------------------
        -- GIVEN-NAME-FIRST: "K-M Aye," or "Klaus-Michael Aye"
        ---------------------------------------------------------
        -- Collect backward from result
        local back_elems = pandoc.List{}
        while #result > 0 do
          local last = result[#result]
          if last.t == "Space" then
            back_elems:insert(1, table.remove(result, #result))
          elseif last.t == "Str" then
            if last.text:match(",$") then
              break -- author separator
            elseif is_name_part(last.text) then
              back_elems:insert(1, table.remove(result, #result))
            else
              break
            end
          else
            break
          end
        end
        -- Remove any leading Space that was between authors
        while #back_elems > 0 and back_elems[1].t == "Space" do
          result:insert(back_elems:remove(1))
        end
        back_elems:insert(pandoc.Str(clean_aye))
        result:insert(pandoc.Strong(pandoc.Inlines(back_elems)))
        if trailing ~= "" then
          result:insert(pandoc.Str(trailing))
        end
        i = i + 1

      else
        -- Standalone "Aye" without clear name context — just bold it
        result:insert(pandoc.Strong{pandoc.Str(clean_aye)})
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
  -- Build citation key -> year mapping from bibliography metadata
  local key_to_year = {}
  local refs = pandoc.utils.references(doc)
  for _, ref in ipairs(refs) do
    if ref.issued and ref.issued["date-parts"] then
      local dp = ref.issued["date-parts"]
      if dp[1] and dp[1][1] then
        key_to_year[ref.id] = tostring(dp[1][1])
      end
    end
  end

  -- Run citeproc to generate the bibliography
  doc = pandoc.utils.citeproc(doc)

  -- Find and restructure the #refs div
  doc.blocks = doc.blocks:walk({
    Div = function(div)
      if div.identifier ~= "refs" then
        return nil
      end

      -- Bold author name and group by year
      local by_year = {}
      local year_order = {}
      for _, elem in ipairs(div.content) do
        if elem.t == "Div" then
          -- Bold "Aye" name variations in each entry
          for bi, block in ipairs(elem.content) do
            if (block.t == "Para" or block.t == "Plain") and block.content then
              elem.content[bi] = pandoc[block.t](bold_aye_name(block.content))
            end
          end

          -- Group by year
          local key = elem.identifier:gsub("^ref%-", "")
          local year = key_to_year[key] or "Unknown"
          if not by_year[year] then
            by_year[year] = {}
            year_order[#year_order + 1] = year
          end
          by_year[year][#by_year[year] + 1] = elem
        end
      end

      -- Sort years descending (newest first)
      table.sort(year_order, function(a, b) return a > b end)

      -- Rebuild div content with year headings
      local new_content = pandoc.Blocks{}
      for _, year in ipairs(year_order) do
        new_content:insert(pandoc.Header(2, pandoc.Str(year), pandoc.Attr("section-" .. year)))
        for _, ref_div in ipairs(by_year[year]) do
          new_content:insert(ref_div)
        end
      end

      div.content = new_content
      return div
    end
  })

  return doc
end
