export default function DashboardLayout(props: { children: React.ReactNode }) {
  return (
    <div className="ml-10 mr-10">
      <div className="justify-center items-center flex flex-col mt-10 gap-5">
        {props.children}
      </div>
    </div>
  );
}
