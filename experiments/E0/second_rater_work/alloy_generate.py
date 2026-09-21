import json, sys
from pathlib import Path

sys.path.insert(0, "/private/tmp/ve-e0-integration")
import ve

ROOT=Path(__file__).resolve().parents[3]
SAMPLE=json.loads((ROOT/"experiments/E0/survey_samples/_drawn/alloy.json").read_text())["sample"]

def env(sorts, preds=(), consts=()):
    constant_names={c for c,_,_ in consts}
    return {"language":"ve.core@0","profile":"relational-fol@0","spec_revision":"ve-v0-draft-2026-09-20","vocabulary":{
      "sorts":{s:{"description":d} for s,d in sorts if s not in constant_names},
      "predicates":{p:{"arguments":a,"description":d} for p,a,d in preds},
      "constants":{c:{"sort":("object" if c == "farmer" and s == "farmer" else s),"description":d} for c,s,d in consts}}}

def fit(i,label,constructs,rationale,source,e,reif):
    E=ve.Environment(e); parsed=ve.check(E,source)
    return {"dataset":"alloy","id":SAMPLE[i]["id"],"label":label,"construct_needed":constructs,"rationale":rationale,"formalization":source,"environment":e,"parse_result":parsed,"reification":reif}

def miss(i,label,constructs,rationale,reif=None):
    return {"dataset":"alloy","id":SAMPLE[i]["id"],"label":label,"construct_needed":constructs,"rationale":rationale,"formalization":None,"environment":None,"parse_result":{"status":"not_applicable","reason":"no faithful v0 formalization for this rating"},"reification":reif}

def neg(a): return f"not ({a})"
def conj(a,b): return f"({a}) and ({b})"
def disj(a,b): return f"({a}) or ({b})"
def impl(a,b): return f"if ({a}), then ({b})"
def fa(sort,var,body): return f"for every {sort} {var}, ({body})"
def ex(sort,var,body): return f"there exists {sort} {var}, ({body})"
def statement(body): return body+".\n"

R=[]
R.append(miss(0,"NO",["transitive_closure","ordered_successor"],"After expanding RingAtTick and graph/ring, the preservation assertion essentially tests reachability and ring structure using reflexive/transitive closure. v0 cannot define that closure, and treating ring_at_tick as atomic would hide the essential claim."))

R.append(miss(1,"OPAQUE",["ternary_relation_reification","relational_join","dependent_lookup"],"The equation composes state-indexed data with two identifier-indexed result fields. A relational skeleton is possible, but a v0 encoding needs several tuple sorts plus totality/functionality axioms; omitting those would admit observations that are not Alloy field values, so this record is conservatively opaque."))

R.append(miss(2,"OPAQUE",["relation_valued_state","set_equality","quaternary_relation"],"LoopFree compares complete time-indexed member/message sets and requires preservation of a five-field message identity. A useful skeleton could quantify distinct ticks, but a compact v0 witness would need named equality-of-slices checks; those checks would be opaque rather than implemented by v0."))
R.append(miss(3,"NO",["transitive_closure","relation_difference"],"less_than is defined by membership in the transitive closure of a cyclic successor relation after deleting edges into from. Reachability is the entire predicate and v0 has no closure operator."))
R.append(miss(4,"NO",["transitive_closure","relation_difference"],"The duplicate less_than definition likewise depends essentially on transitive closure after relation restriction/difference."))
R.append(miss(5,"NO",["general_cardinality","integer_arithmetic","ordered_sequence"],"add expands startsWith/afterLastIdx and requires cardinality equality with integer addition. Unbounded counting and arithmetic are unavailable in v0."))

e=env([("iterator_ref","An iterator reference."),("state","An object state."),("binding","A reified state/reference/object tuple."),("iterator","An iterator object."),("reference","An object reference.")],[("binding_state",["binding","state"],"Binding state."),("binding_ref",["binding","iterator_ref"],"Bound iterator reference."),("binding_iterator",["binding","iterator"],"Bound iterator object."),("left",["iterator","reference"],"Reference remains in the iterator's left set.")])
s="for every iterator_ref r, (for every state s, (there exists binding b, (((b binding_state s) and (b binding_ref r)) and (there exists iterator i, ((b binding_iterator i) and (there exists reference x, (i left x))))))).\n"
R.append(fit(6,"REIFIED",["ternary_relation_reification","existential_quantification"],"hasNext says that the Iterator reached through s.obj[this] has some member in left. A binding atom reifies the state-dependent object lookup.",s,e,"binding represents one tuple of the state-indexed obj field restricted to IteratorRef and Iterator."))

e=env([("snapshot","A river-bank snapshot."),("object","A transported object."),("farmer","The farmer atom."),("choice","A crossing choice object." )],[("before_from",["snapshot","object"],"Object is on source bank before."),("after_from",["snapshot","object"],"Object is on source bank after."),("before_to",["snapshot","object"],"Object is on destination bank before."),("after_to",["snapshot","object"],"Object is on destination bank after."),("eats",["object","object"],"First object eats second."),("chosen",["choice","object"],"Chosen passenger." )],[('farmer','farmer','The unique farmer')])
s="for every snapshot s, (((for every object o, (if (s after_from o), then (((s before_from o) and (not (o equals @farmer))) and (not (there exists object e, ((s after_from e) and (e eats o))))))) and (for every object o, (if ((s before_from o) and ((not (o equals @farmer)) and (not (there exists object e, ((s after_from e) and (e eats o)))))), then (s after_from o)))) and ((for every object o, (if (s after_to o), then ((s before_to o) or (o equals @farmer)))) and (for every object o, (if ((s before_to o) or (o equals @farmer)), then (s after_to o))))) or (there exists choice c, (there exists object x, (((c chosen x) and ((s before_from x) and (not (x equals @farmer)))) and (true)))).\n"
R.append(miss(7,"OPAQUE",["set_parameter_reification","relation_image","set_equality"],"crossRiver relates four set-valued parameters and uses a self-reference to the post-source set inside the eaten-image subtraction. A compact v0 skeleton would conceal extensional equality of these set expressions, so this is conservatively opaque."))

e=env([("train_state","A railway train state."),("segment","A track segment."),("train","A train." )],[("occupied",["train_state","segment"],"Segment recorded occupied."),("on_at",["train","segment"],"Train-to-segment placement in the state represented by this environment.")])
s="for every train_state x, (for every segment s, (if (x occupied s), then (there exists train t, (t on_at s)))).\nfor every train_state x, (for every segment s, (if (there exists train t, (t on_at s)), then (x occupied s))).\n"
R.append(miss(8,"OPAQUE",["ternary_relation_reification","set_comprehension"],"The fact is extensionally first-order, but x.on is state-indexed and needs a reified placement tuple plus completeness and functionality constraints. Omitting that state dimension changes the fact; a compact occupied predicate would therefore hide the defining comprehension."))

R.append(miss(9,"NO",["reflexive_transitive_closure","relation_union","relation_converse"],"Connected is precisely reachability in the undirected parent graph via reflexive transitive closure. No independent non-closure content remains."))
R.append(miss(10,"NO",["general_cardinality","ordered_predecessors","integer_arithmetic"],"copy equates cardinalities of predecessor sets and therefore compares arbitrary indices by counting. v0 lacks general counting and arithmetic."))
R.append(miss(11,"NO",["transitive_closure","acyclicity"],"graph/dag expands to acyclicity via transitive closure; that is the whole fact."))
R.append(miss(12,"OPAQUE",["expanded_helper_predicates","state_transition","relation_override"],"TypeSoundness has a simple implication shell, but RuntimeTypesOK, ExecuteSetter, and TypeChecksSetter expand into substantial Java typing and transition semantics. Naming those checks as unary predicates would hide the essential content."))
R.append(miss(13,"OPAQUE",["fixed_cardinality","transitive_closure","expanded_helpers"],"Exactly one Node is expressible with equality, but NextCorrect expands less_than, whose meaning requires transitive closure. The remaining State.active=Node condition does not capture the purpose independently."))

e=env([("state","A paragraph-numbering state." )],[('numbered',["state"],"State belongs to NumberedState.")])
s="for every state s, (s is numbered).\n"
R.append(fit(14,"DIRECT",["unary_predicate","universal_quantification"],"Because NumberedState is a subsignature of State, State = NumberedState is exactly that every State atom is numbered.",s,e,None))

e=env([("state","A Firewire state."),("link","A Firewire link."),("message","A message."),("queue_binding","A reified state/link/queue-slot observation." )],[("binding_state",["queue_binding","state"],"Observed state."),("binding_link",["queue_binding","link"],"Observed link."),("slot_message",["queue_binding","message"],"Message in the selected queue slot.")])
s="for every state s, (for every link x, (for every message m, (there exists queue_binding b, ((((b binding_state s) and (b binding_link x)) and (b slot_message m)) and (for every message m2, (if (b slot_message m2), then (m2 equals m))))))).\n"
R.append(miss(15,"OPAQUE",["ternary_relation_reification","functional_lookup","parameterized_predicate"],"PeekQueue is representable only after reifying both its invocation relation and the state/link/queue/slot join, with totality and functionality inherited from the source signatures. A formula that merely names peek_queue would hide the join, so this record is conservatively opaque."))

e=env([("element","An Alloy univ atom." )],[("in_s",["element"],"Element belongs to the set parameter s."),("in_r",["element","element"],"Pair belongs to the relation parameter r.")])
s="for every element x, (if (x is in_s), then (there exists element y, ((x in_r y) and (for every element z, (if (x in_r z), then (z equals y)))))).\n"
R.append(fit(16,"REIFIED",["parameter_relationalization","exactly_one"],"For the fixed relation and set parameters, function[r,s] says each in_s element has exactly one in_r image. Existence plus equality of every other image expresses one without counting.",s,e,"in_s and in_r are the supplied extensions of this invocation's set and relation parameters."))
R.append(miss(17,"OPAQUE",["recursive_definition","transitive_closure","expanded_helpers"],"The conjunction expands ClosestPrecedingFinger, FindPredecessor, and FindSuccessor. FindPredecessor is recursively constrained through its own result and the ordering predicates use closure; v0 cannot retain that meaning without opaque helper atoms."))

e=env([("prisoner","A non-counter prisoner."),("state","A game state."),("switch_count","A reified prisoner/state/count tuple."),("integer","An Alloy integer atom." )],[("tuple_prisoner",["switch_count","prisoner"],"Tuple prisoner."),("tuple_state",["switch_count","state"],"Tuple state."),("tuple_value",["switch_count","integer"],"Tuple integer value.")],[('first','state','First ordered state'),('zero','integer','Integer zero')])
s="for every prisoner p, (there exists switch_count t, (((t tuple_prisoner p) and (t tuple_state @first)) and (t tuple_value @zero))).\n"
R.append(fit(18,"REIFIED",["ternary_relation_reification","constants"],"The predicate only fixes every OtherPrisoner's first-state timesSwitched value to zero; it does not perform arithmetic.",s,e,"switch_count reifies the ternary state/prisoner/integer graph entry; first and zero denote the referenced singleton atoms."))

e=env([("state","A light state."),("junction","A junction."),("light","A traffic light."),("color","A color."),("observation","A reified state/light/color tuple." )],[("junction_light",["junction","light"],"Light belongs to junction."),("obs_state",["observation","state"],"Observed state."),("obs_light",["observation","light"],"Observed light."),("obs_color",["observation","color"],"Observed color.")],[('red','color','The Red color')])
s="for every state s, (for every junction j, (for every light a, (for every light b, (if (((j junction_light a) and (j junction_light b)) and ((not (a equals b)) and ((not (there exists observation oa, (((oa obs_state s) and (oa obs_light a)) and (oa obs_color @red)))) and (not (there exists observation ob, (((ob obs_state s) and (ob obs_light b)) and (ob obs_color @red))))))), then (a equals b))))).\n"
R.append(fit(19,"REIFIED",["at_most_one","ternary_relation_reification"],"lone j.lights-redLights[s] means any two non-red lights of j are equal. redLights expands through the state-indexed color field.",s,e,"observation atoms encode color(state,light); pairwise equality implements lone without counting."))

R.append(miss(20,"NO",["transitive_closure","ordered_future","expanded_helpers"],"ord/nexts is transitive future reachability, and CanReceive expands further state-indexed conditions. The future quantification is essential and cannot be expressed by v0."))
R.append(miss(21,"NO",["transitive_closure","expanded_helpers","general_cardinality"],"SameCPF2 expands ordering reachability through less_than and also uses #active=1. Although the latter is expressible, the closest-preceding semantics essentially uses closure."))

e=env([("object","A filesystem object."),("directory","A directory." )],[("contents",["directory","object"],"Directory directly contains object.")],[('root','object','The distinguished root directory')])
s="for every directory d, (not (d contents @root)).\n"
R.append(fit(22,"DIRECT",["binary_predicate","negation","universal_quantification"],"RootTop says no object's contents include Root; only directories possess contents, so universal quantification over directories is exact.",s,e,None))

e=env([("time","An ordered protocol time."),("process","A ring process."),("payload","A process identifier waiting to be sent."),("send_entry","A reified process/time/payload tuple." )],[("entry_time",["send_entry","time"],"Entry time."),("entry_process",["send_entry","process"],"Entry process."),("entry_payload",["send_entry","payload"],"Queued payload."),("next_time",["time","time"],"Immediate successor time." )],[('last','time','Last ordered time')])
s="for every time t, (if (not (t equals @last)), then (if (there exists send_entry e, (e entry_time t)), then (there exists time u, ((t next_time u) and (there exists process p, (there exists payload q, (((there exists send_entry a, (((a entry_time t) and (a entry_process p)) and (a entry_payload q))) and (not (there exists send_entry b, (((b entry_time u) and (b entry_process p)) and (b entry_payload q))))) or ((there exists send_entry b, (((b entry_time u) and (b entry_process p)) and (b entry_payload q))) and (not (there exists send_entry a, (((a entry_time t) and (a entry_process p)) and (a entry_payload q)))))))))))).\n"
R.append(fit(23,"REIFIED",["ternary_relation_reification","set_inequality","ordered_successor"],"progress requires that whenever any toSend entry exists at a non-last time, some process's toSend slice changes at the next time. Set inequality is witnessed by an element in the symmetric difference.",s,e,"send_entry encodes toSend(process,payload,time); next_time exposes only the immediate ordering operation used here."))

e=env([("book","An address-book state."),("name","A name."),("address","An address."),("entry","A reified book/name/address tuple." )],[("entry_book",["entry","book"],"Entry book."),("entry_name",["entry","name"],"Entry name."),("entry_address",["entry","address"],"Entry address.")])
s="for every book b, (for every book b2, (for every name n, (for every address a, ((there exists entry e2, (((e2 entry_book b2) and (e2 entry_name n)) and (e2 entry_address a))) or (not (there exists entry e2, (((e2 entry_book b2) and (e2 entry_name n)) and (e2 entry_address a)))))))).\n"
R.append(miss(24,"OPAQUE",["ternary_relation_reification","relation_difference","set_equality"],"del defines equality of two book-indexed binary relations after removing every tuple with name n. It is mechanically reifiable, but a faithful closed v0 definition also needs an invocation tuple and a full extensional biconditional; a smaller skeleton would omit the frame condition."))

R.append(miss(25,"OPAQUE",["expanded_helpers","relation_valued_state","ordered_predecessor"],"OutsiderCantSend expands IsMember, CanReceive, ReceiveConditions, and several state-indexed relations. A compact formula using those names would hide the essential authorization semantics; fully expanding all relation slices exceeds v0's flat vocabulary without extensive tuple reification."))

e=env([("time","A protocol time."),("process","A process." )],[('elected',["process","time"],"Process is elected at time.")])
s="there exists time t, (there exists process p, (p elected t)).\n"
R.append(fit(26,"DIRECT",["binary_predicate","existential_quantification"],"some t: Time | some elected.t is exactly existence of a time and process related by elected.",s,e,None))

e=env([("unit","A dummy sort unused by the empty predicate." )])
s="true.\n"
R.append(fit(27,"DIRECT",["truth"],"An Alloy predicate with an empty body imposes no constraint, so its formula is true.",s,e,None))

e=env([("state","A Firewire state."),("link","A link."),("message","A message."),("queue_obs","A reified state/link/queue observation." )],[("obs_state",["queue_obs","state"],"Observation state."),("obs_link",["queue_obs","link"],"Observation link."),("slot",["queue_obs","message"],"Slot message."),("overflow",["queue_obs","message"],"Overflow message.")])
s="for every state pre, (for every state post, (for every link x, ((not (there exists queue_obs q, (((q obs_state post) and (q obs_link x)) and ((there exists message m, (q slot m)) or (there exists message m, (q overflow m)))))) and (for every link y, (if (not (y equals x)), then (for every message m, (((there exists queue_obs q1, (((q1 obs_state pre) and (q1 obs_link y)) and ((q1 slot m) or (q1 overflow m)))) or (not (there exists queue_obs q2, (((q2 obs_state pre) and (q2 obs_link y)) and ((q2 slot m) or (q2 overflow m))))))))))))).\n"
R.append(miss(28,"OPAQUE",["ternary_relation_reification","set_equality","frame_condition"],"ReadQueue combines an empty selected post-state queue with extensional equality of every other pre/post queue. The empty selected queue is directly expressible, but a compact skeleton would hide equality of two state-indexed slot/overflow slices."))

e=env([("element","An Alloy univ atom."),("set_member","A membership tuple for s."),("edge_p","A tuple of p."),("edge_q","A tuple of q."),("edge_union","A tuple of p+q." )],[("member",["set_member","element"],"Membership in s."),("source_p",["edge_p","element"],"p source."),("target_p",["edge_p","element"],"p target."),("source_q",["edge_q","element"],"q source."),("target_q",["edge_q","element"],"q target."),("source_union",["edge_union","element"],"union source."),("target_union",["edge_union","element"],"union target.")])
s="for every set_member sm, (for every element y, ((there exists edge_union u, ((u source_union sm) and (u target_union y))) or (not (there exists edge_union u, ((u source_union sm) and (u target_union y)))))).\n"
R.append(miss(29,"NO",["higher_order_quantification","relation_union","relational_image"],"The assertion universally quantifies over arbitrary sets and binary relations. Reifying a fixed relation value is possible, but quantifying over all predicate extensions is genuinely higher-order and is unavailable in v0; the assertion has no independent first-order object-level claim."))

# Revisit state-indexed joins using fixed invocation constants and explicit tuple membership.
e=env([("iterator_ref","An iterator reference."),("state","An object state."),("binding","A reified state/reference/object tuple."),("iterator","An iterator object."),("reference","An object reference.")],[("binding_state",["binding","state"],"Binding state."),("binding_ref",["binding","iterator_ref"],"Bound iterator reference."),("binding_iterator",["binding","iterator"],"Bound iterator object."),("left",["iterator","reference"],"Reference remains in the iterator's left set.")],[('current_ref','iterator_ref','Receiver this'),('current_state','state','Input state s')])
s="there exists binding b, (((b binding_state @current_state) and (b binding_ref @current_ref)) and (there exists iterator i, ((b binding_iterator i) and (there exists reference x, (i left x))))).\n"
R[6]=fit(6,"REIFIED",["ternary_relation_reification","fixed_parameter_constants","existential_quantification"],"For one hasNext invocation, constants bind this and s. The binding tuple expands s.obj[this], and existence of a left reference is the predicate body.",s,e,"binding represents a tuple of the state-indexed obj field; the adapter validates its source one-object multiplicity.")

e=env([("train_state","A railway train state."),("segment","A track segment."),("train","A train."),("placement","A reified state/train/segment tuple." )],[("occupied",["train_state","segment"],"Segment is occupied in the state."),("placement_state",["placement","train_state"],"Placement state."),("placement_train",["placement","train"],"Placed train."),("placement_segment",["placement","segment"],"Placement segment.")])
s="for every train_state x, (for every segment g, (if (x occupied g), then (there exists placement p, (((p placement_state x) and (p placement_segment g)) and (there exists train t, (p placement_train t)))))).\nfor every train_state x, (for every segment g, (if (there exists placement p, ((p placement_state x) and (p placement_segment g))), then (x occupied g))).\n"
R[8]=fit(8,"REIFIED",["ternary_relation_reification","set_comprehension","extensional_biconditional"],"occupied is exactly the image of the state-indexed on field. Placement atoms preserve all three tuple roles, and the two implications expand comprehension equality extensionally.",s,e,"placement atoms represent tuples (state, train, segment); the source field multiplicity remains an adapter validation obligation.")

e=env([("state","A Firewire state."),("link","A Firewire link."),("message","A message."),("queue_obs","A reified state/link/slot tuple." )],[("obs_state",["queue_obs","state"],"Observation state."),("obs_link",["queue_obs","link"],"Observation link."),("slot",["queue_obs","message"],"Slot message.")],[('current_state','state','The predicate input state'),('selected_link','link','The predicate input link'),('expected_message','message','The predicate input message')])
s="there exists queue_obs q, ((((q obs_state @current_state) and (q obs_link @selected_link)) and (q slot @expected_message)) and (for every queue_obs r, (if ((r obs_state @current_state) and (r obs_link @selected_link)), then (for every message m, (if (r slot m), then (m equals @expected_message)))))).\n"
R[15]=fit(15,"REIFIED",["ternary_relation_reification","functional_lookup","fixed_parameter_constants"],"For one predicate invocation, constants bind s, x, and m. Queue observations explicitly expose the composed state.queue[x].slot join, and singleton equality requires the expected message and excludes every different slot value.",s,e,"queue_obs is the tuple graph of the composed lookup; constants bind the invocation parameters rather than asserting the predicate for every possible input.")

e=env([("name","A name."),("address","An address." )],[("old_addr",["name","address"],"Pair belongs to b.addr for this invocation."),("new_addr",["name","address"],"Pair belongs to b2.addr for this invocation.")],[('removed_name','name','Name n to delete')])
s="for every name n, (for every address a, (if (n new_addr a), then ((not (n equals @removed_name)) and (n old_addr a)))).\nfor every name n, (for every address a, (if ((not (n equals @removed_name)) and (n old_addr a)), then (n new_addr a))).\n"
R[24]=fit(24,"REIFIED",["parameter_relationalization","relation_difference","extensional_biconditional"],"For the fixed invocation books, old_addr and new_addr expose their addr extensions. The two implications say exactly that a post pair exists iff it was an old pair whose name is not n, including the complete frame condition.",s,e,"The adapter supplies the two binary relation extensions for b and b2; removed_name binds n.")

e=env([("state","A Firewire state."),("link","A link."),("message","A message."),("queue_obs","A reified state/link queue-content tuple." )],[("obs_state",["queue_obs","state"],"Observation state."),("obs_link",["queue_obs","link"],"Observation link."),("slot",["queue_obs","message"],"Slot message."),("overflow",["queue_obs","message"],"Overflow message.")],[('pre_state','state','Input state'),('post_state','state','Output state'),('selected_link','link','Read link')])
s="not (there exists queue_obs q, (((q obs_state @post_state) and (q obs_link @selected_link)) and ((there exists message m, (q slot m)) or (there exists message m, (q overflow m))))).\nfor every link y, (if (not (y equals @selected_link)), then (for every message m, (if (there exists queue_obs q, (((q obs_state @pre_state) and (q obs_link y)) and (q slot m))), then (there exists queue_obs r, (((r obs_state @post_state) and (r obs_link y)) and (r slot m)))))).\nfor every link y, (if (not (y equals @selected_link)), then (for every message m, (if (there exists queue_obs r, (((r obs_state @post_state) and (r obs_link y)) and (r slot m))), then (there exists queue_obs q, (((q obs_state @pre_state) and (q obs_link y)) and (q slot m)))))).\nfor every link y, (if (not (y equals @selected_link)), then (for every message m, (if (there exists queue_obs q, (((q obs_state @pre_state) and (q obs_link y)) and (q overflow m))), then (there exists queue_obs r, (((r obs_state @post_state) and (r obs_link y)) and (r overflow m)))))).\nfor every link y, (if (not (y equals @selected_link)), then (for every message m, (if (there exists queue_obs r, (((r obs_state @post_state) and (r obs_link y)) and (r overflow m))), then (there exists queue_obs q, (((q obs_state @pre_state) and (q obs_link y)) and (q overflow m)))))).\n"
R[28]=fit(28,"REIFIED",["ternary_relation_reification","set_equality","frame_condition"],"The first statement empties both post-state fields at x. The remaining four implications give both directions of extensional equality for slot and overflow on every other link.",s,e,"queue_obs atoms explicitly carry state and link roles; constants bind the ReadQueue invocation parameters.")

# FindSuccessor for a fixed State: expose each dependent lookup as tuples.
e=env([("node","A Chord node."),("node_data","Node data in the fixed state."),("identifier","A Chord identifier."),("lookup","A node-data/identifier lookup tuple." )],[("active",["node"],"Node belongs to s.active."),("state_data",["node","node_data"],"s.data maps the node to this NodeData."),("lookup_data",["lookup","node_data"],"Lookup receiver."),("lookup_id",["lookup","identifier"],"Lookup argument."),("find_predecessor",["lookup","node"],"find_predecessor result."),("find_successor",["lookup","node"],"find_successor result."),("next_node",["node_data","node"],"NodeData.next result.")])
body=ex("node_data","nd",conj("n state_data nd",ex("lookup","fp",conj(conj("fp lookup_data nd","fp lookup_id i"),ex("node","p",conj("fp find_predecessor p",ex("node_data","pd",conj("p state_data pd",ex("lookup","fs",conj(conj("fs lookup_data nd","fs lookup_id i"),ex("node","q",conj("fs find_successor q","pd next_node q"))))))))))))
s=statement(fa("node","n",impl("n is active",fa("identifier","i",body))))
R[1]=fit(1,"REIFIED",["dependent_lookup_reification","relational_join","fixed_parameter_relationalization"],"For the fixed input state, the formula follows the exact join chain from active n through s.data, find_predecessor[i], s.data again, and next, requiring find_successor[i] to return that same q.",s,e,"lookup tuples encode the identifier-indexed fields; state_data is the fixed state's binary slice. Source one/lone multiplicities are validated by the adapter.")

# crossRiver for one invocation: each set parameter is supplied as a unary extension.
e=env([("object","A river-crossing object." )],[("from_before",["object"],"Member of from."),("from_after",["object"],"Member of from2."),("to_before",["object"],"Member of to."),("to_after",["object"],"Member of to2."),("eats",["object","object"],"First object eats second.")],[('farmer','object','The Farmer atom')])
def eaten(o): return ex("object","e",conj("e is from_after",f"e eats {o}"))
base=lambda o: conj(conj(f"{o} is from_before",neg(f"{o} equals @farmer")),neg(eaten(o)))
def eq_unary(left,right):
    return conj(fa("object","o",impl(left("o"),right("o"))),fa("object","o",impl(right("o"),left("o"))))
opt1=conj(eq_unary(lambda o:f"{o} is from_after",base),eq_unary(lambda o:f"{o} is to_after",lambda o:disj(f"{o} is to_before",f"{o} equals @farmer")))
def opt2_for(x):
    rhs=lambda o:conj(base(o),neg(f"{o} equals {x}"))
    torhs=lambda o:disj(disj(f"{o} is to_before",f"{o} equals @farmer"),f"{o} equals {x}")
    return conj(conj(conj(f"{x} is from_before",neg(f"{x} equals @farmer")),eq_unary(lambda o:f"{o} is from_after",rhs)),eq_unary(lambda o:f"{o} is to_after",torhs))
s=statement(disj(opt1,ex("object","x",opt2_for("x"))))
R[7]=fit(7,"REIFIED",["set_parameter_relationalization","relation_image","extensional_biconditional"],"The four set parameters are supplied extensionally. Each Alloy set equality is expanded in both directions; the two crossing alternatives preserve the Farmer/passenger additions and the post-source eaten-image subtraction exactly.",s,e,"Unary predicates are the fixed invocation's set extensions; eats remains the source binary relation.")

# LoopFree: state slices and message records are reified, with equality expanded extensionally.
e=env([("tick","A protocol tick."),("kds","A key distribution server."),("member","A member."),("message","A data message."),("group","A GSA."),("key","A group key."),("kds_tick","A KDS/tick slice tuple."),("member_tick","A member/tick slice tuple." )],[("kt_kds",["kds_tick","kds"],"Slice KDS."),("kt_tick",["kds_tick","tick"],"Slice tick."),("kt_member",["kds_tick","member"],"Member in slice."),("mt_member",["member_tick","member"],"Slice member."),("mt_tick",["member_tick","tick"],"Slice tick."),("mt_message",["member_tick","message"],"Received message in slice."),("retransmit_time",["message","tick"],"Message retransmitTime."),("sender",["message","member"],"Message sender."),("sent_time",["message","tick"],"Message sentTime."),("gsa_id",["message","group"],"Message gsaID."),("message_key",["message","key"],"Message key.")])
def kmem(k,t,m): return ex("kds_tick","ks",conj(conj(f"ks kt_kds {k}",f"ks kt_tick {t}"),f"ks kt_member {m}"))
def recv(m,t,msg): return ex("member_tick","rs",conj(conj(f"rs mt_member {m}",f"rs mt_tick {t}"),f"rs mt_message {msg}"))
keq=fa("kds","k",fa("member","m",conj(impl(kmem("k","t","m"),kmem("k","u","m")),impl(kmem("k","u","m"),kmem("k","t","m")))))
req=fa("member","m",fa("message","z",conj(impl(recv("m","t","z"),recv("m","u","z")),impl(recv("m","u","z"),recv("m","t","z")))))
same=ex("member","a",conj(conj("z sender a","z2 sender a"),ex("tick","st",conj(conj("z sent_time st","z2 sent_time st"),ex("group","g",conj(conj("z gsa_id g","z2 gsa_id g"),ex("key","ky",conj("z message_key ky","z2 message_key ky"))))))))
msgcond=fa("message","z",impl("z retransmit_time t",ex("message","z2",conj("z2 retransmit_time u",same))))
bad=conj(conj(conj(neg("t equals u"),keq),req),msgcond)
s=statement(neg(ex("tick","t",ex("tick","u",bad))))
R[2]=fit(2,"REIFIED",["ternary_relation_reification","set_equality","record_identity"],"LoopFree denies two distinct ticks with equal membership and received-message slices plus a matching retransmitted message record. Slice equality is expanded both ways, and every compared message field shares an explicitly quantified value.",s,e,"kds_tick and member_tick reify time-indexed set membership; source field multiplicities are adapter-validated.")

# Expanded CanReceive uses ord/prevs[t], an unbounded transitive predecessor set.
R[25]=miss(25,"OPAQUE",["ordered_transitive_predecessors","expanded_can_receive","state_indexed_relations"],"Expanding CanReceive reaches ReceiveConditions, whose clause msg.retransmitTime in ord/prevs[t] asks whether one tick is any strict predecessor of another. util/ordering prevs is transitive reachability, unavailable in v0. Replacing it with a named earlier predicate would hide the decisive receive condition; the surrounding membership and message relations alone are only a skeleton.")

# TypeSoundness expands through Subtype and State.objects to genuine closure operations.
R[12]=miss(12,"OPAQUE",["reflexive_transitive_closure","transitive_closure","relation_override"],"RuntimeTypesOK expands HasType to Subtype, which computes reflexive transitive closure of class/interface xtends. State semantics also defines objects through holds[vars].^reaches, and expression subexprs uses closure. These closure-derived sets are essential to the premise and conclusion; naming subtype or reachable objects would be opaque in v0.")

# ReadQueue preserves Queue atom identity, not merely extensional queue contents.
e=env([("link","A Firewire link."),("queue","A Queue atom."),("message","A message." )],[("old_queue",["link","queue"],"s.queue mapping."),("new_queue",["link","queue"],"s2.queue mapping."),("slot",["queue","message"],"Queue slot."),("overflow",["queue","message"],"Queue overflow.")],[('selected_link','link','Input link x')])
empty=fa("queue","q",impl("@selected_link new_queue q",conj(neg(ex("message","m","q slot m")),neg(ex("message","m","q overflow m")))))
forward=fa("link","y",impl(neg("y equals @selected_link"),fa("queue","q",impl("y old_queue q","y new_queue q"))))
backward=fa("link","y",impl(neg("y equals @selected_link"),fa("queue","q",impl("y new_queue q","y old_queue q"))))
s=statement(empty)+statement(forward)+statement(backward)
R[28]=fit(28,"REIFIED",["parameter_relationalization","queue_identity","frame_condition"],"For the selected link, every post-state Queue atom has empty slot and overflow. For every other link, the two implications make the pre/post queue mappings extensionally equal as mappings to Queue atoms, preserving the source's atom-identity equality.",s,e,"old_queue and new_queue are the two fixed state slices of queue; slot and overflow remain properties of Queue atoms.")

# Iolus ordered-time assertions: materialize the finite ordering rather than treating it as graph reachability.
iolus_env=env([("tick","An Alloy Tick in the supplied finite ordering."),("member","An Iolus Member."),("message","An Iolus DataMessage."),("kds","An Iolus KDS."),("key","An Iolus Key."),("membership","A reified KDS/tick/member tuple."),("receipt","A reified member/tick/message tuple."),("ownership","A reified member/tick/key tuple." )],[("before",["tick","tick"],"Strict total order on Tick."),("immediate_prev",["tick","tick"],"First tick is the immediate predecessor of second."),("membership_kds",["membership","kds"],"Membership tuple KDS."),("membership_tick",["membership","tick"],"Membership tuple tick."),("membership_member",["membership","member"],"Membership tuple member."),("receipt_member",["receipt","member"],"Receipt tuple member."),("receipt_tick",["receipt","tick"],"Receipt tuple tick."),("receipt_message",["receipt","message"],"Receipt tuple message."),("ownership_member",["ownership","member"],"Ownership tuple member."),("ownership_tick",["ownership","tick"],"Ownership tuple tick."),("ownership_key",["ownership","key"],"Ownership tuple key."),("sender",["message","member"],"Message sender."),("sent_time",["message","tick"],"Message sentTime."),("retransmit_time",["message","tick"],"Message retransmitTime."),("message_key",["message","key"],"Message key.")],[('last','tick','Last Tick in the supplied ordering')])

def imember(m,t):
    return ex("membership","mb",conj(conj(f"mb membership_tick {t}",f"mb membership_member {m}"),ex("kds","kd",f"mb membership_kds kd")))
def ireceived(m,t,z):
    return ex("receipt","rc",conj(conj(f"rc receipt_member {m}",f"rc receipt_tick {t}"),f"rc receipt_message {z}"))
def ireceived_prev(m,t,z):
    return ex("tick","p",conj(f"p immediate_prev {t}",ireceived(m,"p",z)))
def iowns(m,t,k):
    return ex("ownership","ow",conj(conj(f"ow ownership_member {m}",f"ow ownership_tick {t}"),f"ow ownership_key {k}"))
def constant_membership(m,t):
    eq_at_prev=ex("tick","p",conj(f"p immediate_prev {t}",conj(impl(imember(m,t),imember(m,"p")),impl(imember(m,"p"),imember(m,t)))))
    first_case=conj(neg(ex("tick","p",f"p immediate_prev {t}")),neg(imember(m,t)))
    return disj(eq_at_prev,first_case)
def receive_conditions(m,t,z):
    prior=neg(ireceived_prev(m,t,z))
    retrans=ex("tick","rt",conj(f"{z} retransmit_time rt",f"rt before {t}"))
    keyok=ex("key","ky",conj(f"{z} message_key ky",iowns(m,t,"ky")))
    return conj(conj(constant_membership(m,t),prior),conj(retrans,keyok))
def can_receive(m,t,z):
    same_sender=ex("member","a",conj(f"{z} sender a","z2 sender a"))
    same_sent=ex("tick","st",conj(f"{z} sent_time st","z2 sent_time st"))
    available=disj(ireceived_prev(m,t,"z2"),receive_conditions(m,t,"z2"))
    return ex("message","z2",conj(conj(same_sender,same_sent),available))
def sender_is_member(z):
    return ex("member","a",conj(f"{z} sender a",ex("tick","st",conj(f"{z} sent_time st",imember("a","st")))))
def both_members_at_send(z,m):
    return ex("member","a",conj(f"{z} sender a",ex("tick","st",conj(f"{z} sent_time st",conj(imember("a","st"),imember(m,"st"))))))

order_axioms=[]
order_axioms.append(statement(fa("tick","a",neg("a before a"))))
order_axioms.append(statement(fa("tick","a",fa("tick","b",fa("tick","c",impl(conj("a before b","b before c"),"a before c"))))))
order_axioms.append(statement(fa("tick","a",fa("tick","b",impl(neg("a equals b"),disj("a before b","b before a"))))))
adj=lambda p,t: conj(f"{p} before {t}",neg(ex("tick","mid",conj(f"{p} before mid",f"mid before {t}"))))
order_axioms.append(statement(fa("tick","p",fa("tick","t",impl(f"p immediate_prev t",adj("p","t"))))))
order_axioms.append(statement(fa("tick","p",fa("tick","t",impl(adj("p","t"),"p immediate_prev t")))))
order_axioms.append(statement(fa("tick","t",neg("@last before t"))))
order_source="".join(order_axioms)

bad=conj(conj(neg(sender_is_member("z")),imember("m","t")),conj(neg(ireceived_prev("m","t","z")),can_receive("m","t","z")))
s=order_source+statement(neg(ex("message","z",ex("member","m",ex("tick","t",bad)))))
R[25]=fit(25,"REIFIED",["finite_order_adapter","ternary_relation_reification","expanded_helpers"],"The finite Tick ordering is supplied as a strict total before relation with immediate_prev defined as adjacency. IsMember, ConstantMembership, ReceiveConditions, and CanReceive are expanded over membership, receipt, ownership, and message-field tuples; the final sentence denies exactly the outsider-send witness.",s,iolus_env,"Tuple sorts encode the time-indexed fields. The order axioms restrict the adapter to legitimate finite Alloy orderings, matching the ordered-trace treatment used for FRET.")

future_claim=fa("message","z",fa("member","m",ex("tick","t",conj(neg("t equals @last"),fa("tick","u",impl("t before u",impl(both_members_at_send("z","m"),can_receive("m","u","z"))))))))
s=order_source+statement(future_claim)
R[20]=fit(20,"REIFIED",["finite_order_adapter","ordered_future","expanded_helpers"],"ord/nexts[t] is the strict future of t in the supplied finite total order. The witness expands both IsMember tests and CanReceive, including ConstantMembership, prior receipt, retransmit-before, and owned-key conditions.",s,iolus_env,"before is a validated strict total Tick order and immediate_prev its adjacency relation; all state-indexed Alloy fields are tuple-reified.")

# mostlyRed for one predicate invocation; s and j are inputs, not universal claims.
e=env([("state","A light state."),("junction","A junction."),("light","A traffic light."),("color","A color."),("observation","A reified state/light/color tuple." )],[("junction_light",["junction","light"],"Light belongs to the junction."),("obs_state",["observation","state"],"Observed state."),("obs_light",["observation","light"],"Observed light."),("obs_color",["observation","color"],"Observed color.")],[('current_state','state','Predicate input state s'),('current_junction','junction','Predicate input junction j'),('red','color','The Red color')])
def is_red(light):
    return ex("observation","ob",conj(conj("ob obs_state @current_state",f"ob obs_light {light}"),"ob obs_color @red"))
two_nonred=conj(conj("@current_junction junction_light a","@current_junction junction_light b"),conj(neg(is_red("a")),neg(is_red("b"))))
s=statement(fa("light","a",fa("light","b",impl(two_nonred,"a equals b"))))
R[19]=fit(19,"REIFIED",["fixed_parameter_constants","at_most_one","ternary_relation_reification"],"Constants bind the predicate inputs s and j. Any two junction lights that are not red in s must be equal, which is exactly lone (j.lights - redLights[s]) without general counting.",s,e,"observation atoms encode color(state,light); source one-color multiplicity is validated by the adapter.")

assert len(R)==30
(ROOT/"experiments/E0/second_rater_work/alloy.jsonl").write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in R))
print(json.dumps({"records":len(R),"labels":{k:sum(x['label']==k for x in R) for k in ['DIRECT','REIFIED','OPAQUE','NO']},"checked":sum(x['parse_result'].get('language')=='accepted' for x in R)},sort_keys=True))
