import { ChildNodeLabel } from "@/features/timeline/components/childNodeLabel";
import { SphereNode } from "@/features/timeline/components/sphereNode";
import type { TimelineNode } from "@/services/types";

interface NodeProps {
  node: TimelineNode;
  onEditNode: (node: TimelineNode) => void;
}

export function ChildNode({ node, onEditNode }: NodeProps) {
  return (
    <div
      className="
        relative group flex flex-col items-center justify-center
        cursor-pointer
        /* SIZE CONTROLS */
        h-[40%]           /* Adjust this % to control size relative to Lane Height */
        aspect-square     /* Forces Width to match Height (Perfect Circle) */
        min-h-[30px]      /* Safety minimum */
        
        /* LAYOUT SAFETY */
        shrink-0          /* Crucial: Prevents circle from getting squashed in flex row */
      "
      onClick={(e) => {
        e.stopPropagation();
        onEditNode(node);
      }}
    >
      <SphereNode />

      <div className="absolute top-full mt-2">
        <ChildNodeLabel text={node.title} />
      </div>
    </div>
  );
}
