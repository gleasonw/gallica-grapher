import { Paper } from "../models/dbStructs";
import { GraphTicket } from "./GraphTicket";

export interface GraphPageState {
  tickets: GraphTicket[];
  yearRange: [number | undefined, number | undefined];
  month?: number;
  grouping: "year" | "month";
  smoothing: number;
  selectedTicket?: number;
}
export interface AddPaperAction {
  type: "add_paper";
  payload: Paper;
}

export interface RemovePaperAction {
  type: "remove_paper";
  payload: Paper["code"];
}

export interface AddTicketAction {
  type: "add_ticket";
  payload: GraphTicket;
}

export interface RemoveTicketAction {
  type: "remove_ticket";
  payload: GraphPageState["selectedTicket"];
}

export interface RemoveExampleTicketsAction {
  type: "remove_example_tickets";
}

export interface SetYearRangeAction {
  type: "set_year_range";
  payload: GraphPageState["yearRange"];
}

export interface SetMonthAction {
  type: "set_month";
  payload: GraphPageState["month"];
}

export interface SetGroupingAction {
  type: "set_grouping";
  payload: GraphPageState["grouping"];
}

export interface SetSmoothingAction {
  type: "set_smoothing";
  payload: GraphPageState["smoothing"];
}

export interface SetSelectedTicketAction {
  type: "set_selected_ticket";
  payload: GraphPageState["selectedTicket"];
}
export function graphStateReducer(
  state: GraphPageState,
  action:
    | AddTicketAction
    | RemoveTicketAction
    | SetYearRangeAction
    | SetMonthAction
    | SetGroupingAction
    | SetSmoothingAction
    | SetSelectedTicketAction
    | RemoveExampleTicketsAction
): GraphPageState {
  switch (action.type) {
    case "add_ticket":
      return {
        ...state,
        tickets: [...state.tickets, action.payload],
      };
    case "remove_ticket":
      return {
        ...state,
        tickets: state.tickets.filter((ticket) => ticket.id !== action.payload),
      };
    case "set_year_range":
      return {
        ...state,
        yearRange: action.payload,
      };
    case "set_month":
      return {
        ...state,
        month: action.payload,
      };
    case "set_grouping":
      return {
        ...state,
        grouping: action.payload,
      };
    case "set_smoothing":
      return {
        ...state,
        smoothing: action.payload,
      };
    case "set_selected_ticket":
      return {
        ...state,
        selectedTicket: action.payload,
      };
    case "remove_example_tickets":
      return {
        ...state,
        tickets: state.tickets.filter((ticket) => !ticket.example),
      };
  }
}
