#!/usr/bin/env fish
echo ""
echo "╔═══════════════════════════════════════╗"
echo "║  Testing Pieces CLI Fish Completions  ║"
echo "╚═══════════════════════════════════════╝"
echo ""

source pieces_fish_completion.fish

function test_completion
    set -l description $argv[1]
    set -l commandline $argv[2]

    echo ""
    echo "🔍 $description"
    echo "   Command: '$commandline<TAB>'"
    echo "   ─────────────────────────────────────────"

    set -l completions (complete -C "$commandline" 2>&1)
    set -l exit_status $status
    if test $exit_status -ne 0
        echo "   ❌ Error during completion:"
        echo "   $completions"
    else if test -z "$completions"
        echo "   ⚠️  No completions available"
    else
        # Parse and format each completion
        set -l count 0
        for line in $completions
            set count (math $count + 1)
            if test $count -gt 10
                echo "   ... (showing first 10 completions)"
                break
            end

            # Split the line into command and description
            set -l parts (string split -m 1 -- \t $line)
            if test (count $parts) -eq 2
                # Format with command and description
                set -l cmd $parts[1]
                set -l desc $parts[2]
                printf "   %-20s %s\n" $cmd "→ $desc"
            else
                # Just the command, no description
                echo "   • $line"
            end
        end
    end
    echo ""
end

test_completion "1. Testing basic command completion:" "pieces "
test_completion "2. Testing 'ask' command options:" "pieces ask -"
test_completion "3. Testing 'list' command with type choices:" "pieces list "
test_completion "4. Testing 'search' command mode option:" "pieces search --mode "
test_completion "5. Testing alias completion (conversation -> chat):" "pieces conversation -"
test_completion "6. Testing 'ask' command options:" "pieces ask"
test_completion "7. Testing 'mcp' command options:" "pieces mcp"
test_completion "8. Testing 'mcp' command options:" "pieces mcp "
test_completion "9. Testing 'mcp start' command options:" "pieces mcp start"

echo "═══════════════════════════════════════"
echo "✅ Fish completion test complete!"
echo ""
